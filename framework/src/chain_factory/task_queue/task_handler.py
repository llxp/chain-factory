from typing import Dict, Union, Callable, List
from datetime import datetime
from time import sleep
from logging import info, debug, warning, error
from threading import Lock
from odmantic import AIOEngine
from inspect import Signature, signature
from asyncio import AbstractEventLoop, ensure_future

from .task_runner import TaskRunner
from .wrapper.list_handler import ListHandler
from .queue_handler import QueueHandler
from .argument_excluder import ArgumentExcluder

# wrapper
from .wrapper.rabbitmq import RabbitMQ, Message, getPublisher
from .wrapper.redis_client import RedisClient
from .wrapper.bytes_io_wrapper import BytesIOWrapper
from .wrapper.interruptable_thread import ThreadAbortException

# settings
from .common.settings import sticky_tasks
from .common.settings import wait_time
from .common.settings import incoming_block_list_redis_key

# common
from .common.task_return_type import ArgumentType, TaskReturnType, TaskRunnerReturnType  # noqa: E501

# models
from .models.mongodb_models import Task, TaskStatus, WorkflowStatus, TaskWorkflowAssociation, Workflow  # noqa: E501


wait_time = int(wait_time)


class TaskHandler(QueueHandler):
    def __init__(
        self,
        namespace: str,
        node_name: str
    ):
        QueueHandler.__init__(self)
        self.ack_lock = Lock()
        self.registered_tasks: Dict[str, TaskRunner] = {}
        self.mongodb_client: AIOEngine = None
        self.task_timeout = None
        self.namespace = namespace
        self.node_name = node_name
        self._current_task = None

    async def init(
        self,
        mongodb_client: AIOEngine,
        redis_client: RedisClient,
        queue_name: str,
        wait_queue_name: str,
        blocked_queue_name: str,
        loop: AbstractEventLoop,
        rabbitmq_url: str,
    ):
        self.loop = loop
        self.mongodb_client = mongodb_client
        await QueueHandler.init(self, url=rabbitmq_url, queue_name=queue_name, loop=loop)  # noqa: E501
        self.wait_queue_name = wait_queue_name
        self.blocked_queue_name = blocked_queue_name

        await self._init_amqp_publishers(rabbitmq_url)
        self.block_list = ListHandler(list_name=incoming_block_list_redis_key, redis_client=redis_client)  # noqa: E501
        await self.block_list.init()

    def update_task_timeout(self):
        for task in self.registered_tasks:
            task_runner = self.registered_tasks[task]
            task_runner.task_timeout = self.task_timeout

    async def _init_amqp_publishers(self, url: str):
        self.rabbitmq_wait: RabbitMQ = getPublisher(rabbitmq_url=url, queue_name=self.wait_queue_name)  # noqa: E501
        await self.rabbitmq_wait.init()
        self.amqp_planned: RabbitMQ = getPublisher(
            rabbitmq_url=url,
            queue_name="dlx." + self.wait_queue_name,
            queue_options={"x-dead-letter-exchange": "dlx." + self.queue_name, "x-dead-letter-routing-key": self.queue_name}  # noqa: E501
        )
        await self.amqp_planned.init()
        self.amqp_blocked: RabbitMQ = getPublisher(rabbitmq_url=url, queue_name=self.blocked_queue_name)  # noqa: E501
        await self.amqp_blocked.init()

    async def _check_blocklist(self, task: Task, message: Message) -> bool:
        """
        Check the redis blocklist for the node name and task
        """
        blocklist = await self.block_list.get()
        if blocklist is None or blocklist.list_items is None:
            # the blocklist couldn't be retrieved from redis,
            # so rejecting every incoming task
            warning("could not retrieve blocklist from redis, rejecting all tasks")  # noqa: E501
            await self.nack(message)
            sleep(wait_time)
            return True
        for item in blocklist.list_items:
            node_name = item.name
            task_name = item.content
            if task_name == task.name and node_name in [self.node_name, "*"]:  # noqa: E501
                info(f"task '{task.name}' is in block list, ""dispatching to blocked_queue")  # noqa: E501
                task.update_time()
                # reschedule task, which is in incoming block list
                await self.send_to_queue(task, self.amqp_blocked)
                await self.ack(message)
                return True
        return False

    async def _save_workflow(self, workflow_id: str, tags: List[str]):
        """
        Report the workflow id to the mongodb database
        """
        await self.mongodb_client.save(Workflow(
            workflow_id=workflow_id,
            node_name=self.node_name,
            namespace=self.namespace,
            tags=tags,
        ))

    async def _save_task_workflow_association(self, task: Task):
        """
        Report the assignment from workflow_id to task_id to the database
        """
        arguments_excluder = ArgumentExcluder(task.arguments)
        arguments_excluder.exclude()
        task.arguments = arguments_excluder.arguments
        await self.mongodb_client.save(TaskWorkflowAssociation(
            workflow_id=task.workflow_id,
            task=task,
            node_name=self.node_name
        ))
        if arguments_excluder.arguments_copy:
            task.arguments = arguments_excluder.arguments_copy

    async def _run_task(self, task: Task) -> TaskRunnerReturnType:
        """
        Runs the specified task and returns the result of the task function
        """
        task_id = task.task_id
        task_name = task.name
        # buffer to redirect stdout/stderr to the database
        log_buffer = BytesIOWrapper(task_id, task.workflow_id, self.mongodb_client, loop=self.loop)  # noqa: E501
        self._current_task = task
        self._can_be_marked_as_stopped = True
        info(f"running task '{task_name}' with task_id '{task_id}'")
        # run the task
        result = await self.registered_tasks[task_name].run(task.arguments, task.workflow_id, log_buffer)  # noqa: E501
        info(f"task '{task_name}' with task_id {task_id} finished")
        return result

    def _new_task_from_result(self, task_result: TaskReturnType, new_arguments: Dict[str, str]) -> Task:  # noqa: E501
        # check, if result is a string ==> task name
        if isinstance(task_result, str):
            # create a new task object from task name and arguments
            # and return it
            return Task(name=task_result, arguments=new_arguments)
        # check, if result is of type Task ==> task object
        if isinstance(task_result, Task):
            # return the task object
            return task_result
        # check, if result is a registered callable
        if callable(task_result):
            # create a new task object and return it
            return Task(name=task_result.__name__, arguments=new_arguments)
        return None

    def _return_new_task(
        self,
        old_task: Task,
        new_arguments: Dict[str, str],
        task_result: Union[str, Task, Callable[..., Dict[str, str]]],
    ) -> Task:
        """
        add the old task to the current task as the parent and schedule
        the to be scheduled task to the message queue
        """
        new_task = self._new_task_from_result(task_result, new_arguments)
        new_task.set_parent_task(old_task)
        if sticky_tasks:  # settings.sticky_tasks
            # if sticky_tasks option is set,
            # only execute the full workflow on the node it started on
            new_task.node_names = [self.node_name]
        return new_task

    async def _return_error_task(self, task: Task, new_arguments: Dict[str, str]) -> None:  # noqa: E501
        """
        Reenqueue the current task to the wait queue if the current task failed
        """
        # update received date
        task.update_time()
        # accociate the current task with the next task
        task.set_as_parent_task()
        # remove current task id on error
        # generate a new one on next run
        task.cleanup_task()
        task.arguments = new_arguments
        # send task to wait queue
        await self.rabbitmq_wait.send(task.json())
        return None

    async def _save_first_task_as_workflow(self, task: Task):
        if not task.has_parent_task():
            # report workflow to database,
            # if it is the first task in the workflow task chain
            await self._save_workflow(task.workflow_id, task.tags)

    async def _save_task_result(self, task_id: str, result: str):
        task_status = TaskStatus(
            task_id=task_id,
            namespace=self.namespace,
            status=result,
            created_date=datetime.utcnow()
        )
        await self.mongodb_client.save(task_status)

    async def _mark_workflow_as_stopped(self, workflow_id: str, status: str):
        if not await WorkflowStatus.get(self.mongodb_client, workflow_id, self.namespace):  # noqa: E501
            workflow_status = WorkflowStatus(
                workflow_id=workflow_id,
                namespace=self.namespace,
                status=status,
                created_date=datetime.utcnow(),
            )
            await self.mongodb_client.save(workflow_status)

    async def _handle_workflow_stopped(self, result: str, task: Task, can_be_marked_as_stopped: bool):  # noqa: E501
        await self._save_task_result(task.task_id, result)
        if can_be_marked_as_stopped:
            # None means, the workflow chain stops
            await self._mark_workflow_as_stopped(task.workflow_id, result)
        return None  # do nothing

    async def _handle_repeat_task(self, task: Task, arguments: ArgumentType, result: str):  # noqa: E501
        await self._save_task_result(task.task_id, result)
        # the result is False, indicating an error
        # => schedule the task to the waiting queue
        return await self._return_error_task(task, arguments)

    async def _handle_task_result(
        self,
        task_result: Union[bool, None, Task],
        arguments: Dict[str, str],
        message: Message,
        task: Task,
    ) -> Union[Task, None]:
        await self.ack(message)
        if task_result is False:
            return await self._handle_repeat_task(task, arguments, "False")
        elif task_result is TimeoutError:
            if self.registered_tasks[task.name].task_repeat_on_timeout:
                return self._handle_repeat_task(task, arguments, "Timeout")
            return await self._handle_workflow_stopped(
                "Timeout", task, self._can_be_marked_as_stopped)
        elif task_result is ThreadAbortException:
            return await self._save_task_result(task.task_id, "Aborted")
        elif task_result is KeyboardInterrupt:
            return await self._save_task_result(task.task_id, "Stopped")
        else:  # task_result now can only be Task/None/Exception
            if task_result is None:
                return await self._handle_workflow_stopped("None", task, self._can_be_marked_as_stopped)  # noqa: E501
            # Exception means an exception occured during the task run
            elif task_result is Exception:
                return await self._handle_workflow_stopped("Exception", task, self._can_be_marked_as_stopped)  # noqa: E501
            # Task means, a new/next task has been returned,
            # to be scheduled to the queue
            elif task_result is Task:
                await self._save_task_result(task.task_id, "Task")
                return self._return_new_task(task, arguments, task_result)
            else:
                raise Exception(f"Unknown task result, {task_result}")

    async def _prepare_task_in_database(self, task: Task):
        await self._save_first_task_as_workflow(task)
        # associate task id with workflow id in database
        await self._save_task_workflow_association(task)

    async def _prepare_task(self, task: Task):
        """
        Generates a task id and saves the association to it in the database
        """
        task.generate_task_id()
        await self._prepare_task_in_database(task)
        return task

    async def _handle_run_task(
        self,
        task: Task,
        message: Message
    ) -> Union[Task, None]:
        """
        will be executed, when the task is valid,
        which means it has a valid workflow id
        - generates a unique task id and
        - saves the association to the workflow in the database
        - runs the task
        - returns a function to handle the task result
        """
        task_runner_result = await self._run_task(task)
        if task_runner_result:
            task_result, arguments = task_runner_result
            # handle task result and return new Task
            return await self._handle_task_result(task_result, arguments, message, task)  # noqa: E501
        else:
            # error occured converting the arguments from Dict[str, str]
            # to Dict[str, Any] -> to the actual type expected from the task
            error("An Error occured during the task run")
            return None

    async def _handle_planned_task(self, task: Task, message: Message):
        """
        sends the task to the delayed queue with an ttl of planned_date - now
        """
        # TODO: not implemented yet
        error("planning tasks is not implemented yet")
        return None

    async def _handle_task(
        self,
        task: Task,
        message: Message
    ) -> Union[None, Task]:
        """
        Runs a precheck, to see if the task already has a valid workflow id
        if not, it will generate a unique workflow id
        and return it to the queue
        """
        if task.workflow_precheck():
            return await self._prepare_workflow(task, message)
        task = await self._prepare_task(task)
        if await task.is_stopped(self.namespace, self.mongodb_client):
            return await self._handle_stopped(task, message)
        if task.is_planned_task():
            return await self._handle_planned_task(task, message)
        return await self._handle_run_task(task, message)

    async def _prepare_workflow(self, task: Task, message: Message):
        # workflow id does not yet exist
        await self.ack(message)
        # so generate a new workflow id and attach it to the task
        task.generate_workflow_id()
        return task

    async def _handle_stopped(self, task: Task, message: Message):
        debug("TaskHandler::_handle_stopped")
        await self._save_task_result(task.task_id, "Stopped")
        await self.ack(message)
        return None

    async def _send_to_queue(self, queue: RabbitMQ, message: Message, task: Task):  # noqa: E501
        await self.ack(message)
        await queue.send(task.json())

    async def _handle_rejected(self, requested_task: Task, message: Message):
        """
        Increases the reject counter and requeues the task to the message queue
        """
        # task rejected, increase reject counter
        requested_task.increase_rejected()
        if requested_task.check_rejected():
            requested_task.reset_rejected()
            await self._send_to_queue(
                self.rabbitmq_wait, message, requested_task)
        else:
            await self._send_to_queue(self.rabbitmq, message, requested_task)
        return None

    async def check_rejected_task(self, task: Task, message: Message):
        """
        Checks if the task has been rejected too often
        """
        task_rejected = task.check_node_filter(self.node_name)
        if task_rejected:
            task_json = task.json()
            debug("task_rejected, because current node is not in the node_names list: " + task_json)  # noqa: E501
            return await self._handle_rejected(task, message)

    async def on_task(self, task: Task, message: Message) -> Union[None, Task]:
        """
        The callback function, which will be called from the rabbitmq library
        It deserializes the amqp message and then
        checks, if the requested taks is registered and calls it.
        If the task name is on the blocklist,
        it will be rejected, rescheduled and then wait for some time

        Returns either None or a new task
        """
        debug("on_task")
        if task_rejected := await self.check_rejected_task(task, message):
            debug("task_rejected")
            return task_rejected

        if not await self._check_blocklist(task, message):
            debug("task not blocked")
            # task is not on the block list
            # iterate through list of all registered tasks
            for registered_task in self.registered_tasks:
                debug("registered_task: " + registered_task)
                if registered_task == task.name:
                    # reset reject_counter when task has been accepted
                    task.reject_counter = 0
                    return await self._handle_task(task, message)
            # task not found on the current node
            # rejecting task
            info(f"rejecting task: {task.name}")
            return await self._handle_rejected(task, message)
        # task is on the block list
        # return None to indicate no next task should be scheduled
        return None

    def add_task(self, name: str, callback: Signature, repeat_on_timeout: bool):  # noqa: E501
        """
        Register a new task/task function
        """
        task = TaskRunner(name, callback, self.namespace)
        task.task_repeat_on_timeout = repeat_on_timeout
        self.registered_tasks[name] = task
        self.add_schedule_task_shortcut(name, callback)
        debug(f"registered task:{name}")

    def add_schedule_task_shortcut(self, name: str, callback: Signature):
        """
        Add a function to the registered function named .s()
        to schedule the function with or without arguments
        """
        async def schedule_task(*args, **kwargs):
            debug(f"schedule_task: {name}")
            if (args and len(args) > 0):
                # create kwargs from args
                # get keywords from registered callback function
                keywords = signature(callback).parameters
                # create dict from args
                kwargs_args = dict(zip(keywords, args))
                # add kwargs to kwargs_args
                kwargs.update(kwargs_args)
            task = Task(name=name, arguments=kwargs)
            task.set_parent_task(self._current_task)
            debug(f"scheduled task:{task.json()}")
            self._can_be_marked_as_stopped = False
            coroutine = self.send_to_queue(task, self.rabbitmq)
            ensure_future(coroutine, loop=self.loop)

        setattr(callback, "s", schedule_task)
        return schedule_task

    def task_set_redis_client(self, redis_client: RedisClient):
        for task_name in self.registered_tasks:
            task_runner: TaskRunner = self.registered_tasks[task_name]
            task_runner.namespace = self.namespace
            task_runner.set_redis_client(redis_client)
