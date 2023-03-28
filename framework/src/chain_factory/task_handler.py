from typing import Dict, Optional, Type
from typing import Union
from typing import List
from datetime import datetime
from time import sleep
from logging import info
from logging import debug
from logging import warning
from logging import error
from odmantic import AIOEngine
from inspect import signature
from asyncio import AbstractEventLoop
from asyncio import ensure_future

# direct imports
from .task_runner import TaskRunner
from .queue_handler import QueueHandler
from .argument_excluder import ArgumentExcluder

# wrapper
from .wrapper.rabbitmq import RabbitMQ
from .wrapper.rabbitmq import Message
from .wrapper.rabbitmq import getPublisher
from .wrapper.redis_client import RedisClient
from .wrapper.bytes_io_wrapper import BytesIOWrapper
from .wrapper.interruptable_thread import ThreadAbortException
from .wrapper.list_handler import ListHandler

# settings
from .common.settings import sticky_tasks
from .common.settings import wait_time
from .common.settings import max_task_age_wait_queue
from .common.settings import incoming_block_list_redis_key

# data types
from .models.mongodb_models import ArgumentType
from .models.mongodb_models import TaskReturnType
from .models.mongodb_models import TaskRunnerReturnType
from .models.mongodb_models import CallbackType
from .models.mongodb_models import ErrorCallbackType
from .models.mongodb_models import ErrorCallbackMappingType

# models
from .models.mongodb_models import Task
from .models.mongodb_models import TaskStatus
from .models.mongodb_models import WorkflowStatus
from .models.mongodb_models import TaskWorkflowAssociation
from .models.mongodb_models import Workflow


class TaskHandler(QueueHandler):
    def __init__(
        self,
        namespace: str,
        node_name: str
    ):
        QueueHandler.__init__(self)
        self.registered_tasks: Dict[str, TaskRunner] = {}
        self.error_handlers: ErrorCallbackMappingType = {}
        self.mongodb_client: Union[AIOEngine, None] = None
        self.task_timeout: int = -1
        self.namespace: str = namespace
        self.node_name: str = node_name
        self._current_task: Union[Task, None] = None

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
        """
        Initialize the task handler
        there is this extra init function, because the __init__ function
        does not support async functions
        """
        # the loop is needed for the rabbitmq connection,
        # the mongodb connection and to run the task threads
        self.loop = loop
        self.mongodb_client = mongodb_client

        # setting the queue names
        self.wait_queue_name = wait_queue_name
        self.blocked_queue_name = blocked_queue_name

        # Initialize the queue handler
        await QueueHandler.init(
            self, url=rabbitmq_url, queue_name=queue_name, loop=loop)

        # Initialize the amqp publishers,
        # to send messages to the wait and blocked queue
        await self._init_amqp_publishers(rabbitmq_url)

        # Initialize the block list,
        # which can be specified in redis to block
        # either specific tasks on a node or
        # completely the node from receiving tasks
        self.block_list = ListHandler(
            list_name=incoming_block_list_redis_key,
            redis_client=redis_client
        )
        await self.block_list.init()

    def update_task_timeout(self):
        """
        Update the task timeout value for all registered tasks
        """
        for _, runner in self.registered_tasks.items():
            runner.update_task_timeout(self.task_timeout)

    def update_error_handlers(self):
        """
        Update the error handlers for all registered tasks
        """
        for _, runner in self.registered_tasks.items():
            runner.update_error_handlers(self.error_handlers)

    async def _init_amqp_publishers(self, url: str):
        """
        Initialize the amqp publishers,
        to send messages to the wait and blocked queue
        """
        # Initialize the amqp publisher,
        # to send messages to the wait queue
        self.amqp_wait: RabbitMQ = getPublisher(
            rabbitmq_url=url,
            queue_name="dlx." + self.wait_queue_name,
            loop=self.loop,
            queue_options={
                # publish dead lettered messages to the task queue again
                "x-dead-letter-exchange": self.queue_name,
                "x-dead-letter-routing-key": self.queue_name,
                # dead letter messages after max_task_age_wait_queue (seconds * 1000 milliseconds)  # noqa: E501
                "x-message-ttl": max_task_age_wait_queue * 1000,
            }
        )
        await self.amqp_wait.init()
        # Initialize the amqp publisher,
        # to send messages to the blocked queue
        self.amqp_blocked: RabbitMQ = getPublisher(
            rabbitmq_url=url,
            queue_name="dlx." + self.blocked_queue_name,
            loop=self.loop,
            queue_options={
                # publish dead lettered messages to the task queue again
                "x-dead-letter-exchange": self.queue_name,
                "x-dead-letter-routing-key": self.queue_name,
                # dead letter messages after max_task_age_wait_queue (seconds * 1000 milliseconds)  # noqa: E501
                "x-message-ttl": max_task_age_wait_queue * 1000,
            }
        )
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
            # if the blocklist couldn't be retrieved from redis,
            # wait for 5 seconds and try again
            sleep(wait_time)
            return True
        # check if the task is in the blocklist
        for item in blocklist.list_items:
            node_name = item.name
            task_name = item.content
            if task_name == task.name and node_name in [self.node_name, "*"]:  # noqa: E501
                info(f"task '{task.name}' is in block list, ""dispatching to blocked_queue")  # noqa: E501
                task.update_time()
                # reschedule task, which is in incoming block list
                await self.send_to_queue(task, self.amqp_blocked)
                # and acknowledge the message to remove it from the queue
                await self.ack(message)
                return True
        return False

    async def _save_workflow(self, workflow_id: str, tags: List[str]):
        """
        Report the workflow id to the mongodb database
        """
        if self.mongodb_client is not None:
            # save the workflow to the database
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
        # the argument excluder is used to filter out specific arguments,
        # which should not be saved in the database (e.g. passwords)
        # can be specified using the hidden argument "exclude"
        arguments_excluder = ArgumentExcluder(task.arguments)
        # exclude the arguments
        arguments_excluder.exclude()
        # override the arguments with the filtered arguments
        task.arguments = arguments_excluder.arguments
        if self.mongodb_client is not None:
            # save the task workflow association
            await self.mongodb_client.save(TaskWorkflowAssociation(
                workflow_id=task.workflow_id,
                task=task,
                node_name=self.node_name
            ))
        # restore the arguments
        if arguments_excluder.arguments_copy:
            task.arguments = arguments_excluder.arguments_copy

    async def _run_task(self, task: Task, workflow: Optional[Workflow]) -> TaskRunnerReturnType:  # noqa: E501
        """
        Runs the specified task and returns the result of the task function
        """
        task_id: str = task.task_id or ""
        task_name = task.name
        if self.mongodb_client is None:
            raise Exception("mongodb client is not initialized")
        # buffer to redirect stdout/stderr to the database
        log_buffer = BytesIOWrapper(task_id, task.workflow_id, self.mongodb_client, loop=self.loop)  # noqa: E501
        self._current_task = task
        self._can_be_marked_as_stopped = True
        info(f"running task '{task_name}' with task_id '{task_id}'")
        # run the task, the loop has already been set in the constructor of the TaskRunner  # noqa: E501
        result = await self.registered_tasks[task_name].run(workflow, task, log_buffer)  # noqa: E501
        info(f"task '{task_name}' with task_id {task_id} finished")
        return result

    def _new_task_from_result(self, task_result: TaskReturnType, new_arguments: ArgumentType) -> Union[Task, None]:  # noqa: E501
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
        new_arguments: ArgumentType,
        task_result: TaskReturnType,
    ) -> Task:
        """
        add the old task to the current task as the parent and schedule
        the to be scheduled task to the message queue
        """
        new_task = self._new_task_from_result(task_result, new_arguments)
        if new_task is None:
            raise Exception("invalid task result")
        # set the parent task to connect the tasks in the database
        # to the workflow
        new_task.set_parent_task(old_task)
        if sticky_tasks:  # settings.sticky_tasks
            # if sticky_tasks option is set,
            # only execute the full workflow on the node it started on
            new_task.node_names = [self.node_name]
        return new_task

    async def _return_error_task(self, task: Task, new_arguments: ArgumentType) -> None:  # noqa: E501
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
        await self.amqp_wait.send(task.json())
        return None

    async def _save_first_task_as_workflow(self, task: Task):
        """
        Report the first task in the workflow as the workflow to the database
        """
        # if the task has no parent task it is the first task in the workflow
        if not task.has_parent_task():
            # report workflow to database,
            # if it is the first task in the workflow task chain
            await self._save_workflow(task.workflow_id, task.tags or [])

    async def _save_task_result(self, task_id: str, result: str):
        """
        Report the result of the task to the database
        """
        # create a task status/result object
        task_status = TaskStatus(
            task_id=task_id,
            namespace=self.namespace,
            status=result,
            created_date=datetime.utcnow()
        )
        if self.mongodb_client is None:
            raise Exception("mongodb client is not initialized")
        # save the task status/result object to the database
        await self.mongodb_client.save(task_status)

    async def _mark_workflow_as_stopped(self, workflow_id: str, status: str):
        """
        Report the workflow as stopped to the database
        """
        if self.mongodb_client is None:
            raise Exception("mongodb client is not initialized")
        # check, if the workflow is already marked as stopped
        if not await WorkflowStatus.get(self.mongodb_client, workflow_id, self.namespace):  # noqa: E501
            # if the workflow is not marked as stopped, mark it as stopped
            workflow_status = WorkflowStatus(
                workflow_id=workflow_id,
                namespace=self.namespace,
                status=status,
                created_date=datetime.utcnow(),
            )
            # save the workflow status to the database
            await self.mongodb_client.save(workflow_status)

    async def _handle_workflow_stopped(self, result: str, task: Task, can_be_marked_as_stopped: bool):  # noqa: E501
        """
        Handle the result of a task, if the workflow is stopped
        """
        # save the task result to the database
        await self._save_task_result(task.task_id, result)
        # if theworkflow is stopped, and no .s() call was made
        # mark the workflow as stopped
        if can_be_marked_as_stopped:
            # None normally means, the workflow chain stops
            # exception: an .s() call was made,
            # then this stage is skipped and not the last
            await self._mark_workflow_as_stopped(task.workflow_id, result)
        return None  # do nothing, if the workflow is not yet stopped

    async def _handle_repeat_task(self, task: Task, arguments: ArgumentType, result: str):  # noqa: E501
        await self._save_task_result(task.task_id, result)
        # the result is False, indicating an error
        # => schedule the task to the waiting queue
        return await self._return_error_task(task, arguments)

    async def _handle_task_result(
        self,
        task_result: TaskReturnType,
        arguments: ArgumentType,
        message: Message,
        task: Task,
    ) -> Union[Task, None]:
        """
        Handle the result of a task, if the task is finished running
        """
        # ack the task in rabbitmq, to remove it from the queue
        await self.ack(message)

        # check, if the task is False, which means,
        # the task failed and should be repeated
        if task_result is False:
            return await self._handle_repeat_task(task, arguments, "False")

        # check, if the task result is a TimeoutError,
        # which means, there is configured a maximum time a task can run
        elif task_result is TimeoutError:
            if self.registered_tasks[task.name].task_repeat_on_timeout:
                return await self._handle_repeat_task(task, arguments, "Timeout")  # noqa: E501
            return await self._handle_workflow_stopped("Timeout", task, self._can_be_marked_as_stopped)  # noqa: E501

        # check, if the task result is a ThreadAbortException,
        # which means, the task was aborted using a redis broadcast
        # "abort" command
        elif task_result is ThreadAbortException:
            debug("ThreadAbortException")
            return await self._save_task_result(task.task_id, "Aborted")

        # check, if the task result is a KeyboardInterrupt,
        # which means, the task was aborted using a redis broadcast
        # "stop" command
        elif task_result is KeyboardInterrupt:
            return await self._save_task_result(task.task_id, "Stopped")

        # task_result now can only be Task/None/Exception
        else:
            # None means,
            # there has been no error and no new task should be scheduled
            # => mark the workflow as stopped
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

            # if the task result is not
            # None,
            # Task,
            # Exception,
            # ThreadAbortException,
            # KeyboardInterrupt,
            # TimeoutError
            # or False
            # raise an exception
            else:
                raise Exception(f"Unknown task result, {task_result}")

    async def _prepare_task_in_database(self, task: Task):
        """
        Generates a task id and saves the association to it in the database
        """
        await self._save_first_task_as_workflow(task)
        # associate task id with workflow id in database
        await self._save_task_workflow_association(task)

    async def _prepare_task(self, task: Task):
        """
        Generates a task id and saves the association to it in the database
        """
        # generate a new task id
        task.generate_task_id()
        # save the task to the database
        await self._prepare_task_in_database(task)
        # return the prepared task
        return task

    async def _get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """
        Get the workflow from the database
        """
        if self.mongodb_client is None:
            raise Exception("mongodb client is not initialized")
        workflow = await self.mongodb_client.find_one(
            Workflow,
            (
                (Workflow.workflow_id == workflow_id) &
                (Workflow.namespace == self.namespace)
            )
        )
        if workflow is None:
            error(f"Workflow {workflow_id} not found")
            return
        return workflow

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
        workflow = await self._get_workflow(task.workflow_id)
        task_runner_result = await self._run_task(task, workflow)
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
        # planned tasks are not implemented yet
        error("planning tasks is not implemented yet")
        return None

    async def _handle_incoming_task(
        self,
        task: Task,
        message: Message
    ) -> Union[None, Task]:
        """
        Runs a precheck, to see if the task already has a valid workflow id
        if not, it will generate a unique workflow id
        and return it to the queue
        The return here will be handled by the on_task method,
        which in turn will return it to the QueueHandler
        """
        debug(f"handle task {task}")
        if self.mongodb_client is None:
            raise Exception("mongodb client is None")

        debug("workflow_precheck")
        # check, if the task is the first task of a workflow
        if task.workflow_precheck():
            debug("prepare workflow")
            return await self._prepare_workflow(task, message)

        debug("prepare task")
        task = await self._prepare_task(task)
        debug("is_stopped")
        if await task.is_stopped(self.namespace, self.mongodb_client):
            debug("task is stopped. handle_stopped")
            return await self._handle_stopped(task, message)

        debug("is_planned_task")
        if task.is_planned_task():
            debug("task is planned. handle_planned_task")
            return await self._handle_planned_task(task, message)

        debug("handle_run_task")
        return await self._handle_run_task(task, message)

    async def _prepare_workflow(self, task: Task, message: Message):
        """
        Removes the hollow task from the queue
        and returns a new task with a new workflow id
        and returns it to the queue
        """
        # remove the task from the queue
        await self.ack(message)
        # generate a new workflow id and attach it to the task
        task.generate_workflow_id()
        # return means to the rabbitmq wrapper,
        # the task will be pushed to the queue
        # the return will directly be passed back to the RabbitMQ wrapper
        return task

    async def _handle_stopped(self, task: Task, message: Message):
        debug("TaskHandler::_handle_stopped")
        await self._save_task_result(task.task_id, "Stopped")
        await self.ack(message)
        return None

    async def _send_to_queue(self, queue: Union[RabbitMQ, None], message: Message, task: Task):  # noqa: E501
        await self.ack(message)
        if queue is None:
            raise Exception("_send_to_queue: RabbitMQ is None")
        await queue.send(task.json())

    async def _handle_rejected(self, requested_task: Task, message: Message):
        """
        Increases the reject counter and requeues the task to the message queue
        """
        # task rejected, increase reject counter
        requested_task.increase_rejected()
        if requested_task.check_rejected():
            requested_task.reset_rejected()
            await self._send_to_queue(self.amqp_wait, message, requested_task)  # noqa: E501
            # await self._send_to_queue(self.rabbitmq_wait, message, requested_task)  # noqa: E501
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
                debug(f"registered_task: {registered_task} == {task.name}")
                if registered_task == task.name:
                    # reset reject_counter when task has been accepted
                    task.reject_counter = 0
                    return await self._handle_incoming_task(task, message)
            # task not found on the current node
            # rejecting task
            info(f"rejecting task: {task.name}")
            return await self._handle_rejected(task, message)
        # task is on the block list
        # return None to indicate no next task should be scheduled
        return None

    def add_task(self, name: str, callback: CallbackType, repeat_on_timeout: bool):  # noqa: E501
        """
        Register a new task/task function
        """
        task = TaskRunner(name, callback, self.namespace)
        task.update_task_repeat_on_timeout(repeat_on_timeout)
        self.registered_tasks[name] = task
        self.add_schedule_task_shortcut(name, callback)
        debug(f"registered task: {name}")

    def add_error_handler(self, exc_type: Type[Exception], callback: ErrorCallbackType):  # noqa: E501
        """
        Register a new error handler

        :param callback: the callback function
        :type callback: Callable[[Task, Exception], None]
        """
        self.error_handlers[exc_type] = callback
        debug("registered error handler for type: " + str(exc_type))

    def clear_error_handlers(self):
        """
        Clear all registered error handlers
        """
        self.error_handlers = {}
        debug("cleared error handlers")

    def add_schedule_task_shortcut(self, name: str, callback: CallbackType):
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
            if self._current_task is None:
                raise Exception("self.current_task has been not set while scheduling a task")  # noqa: E501
            task.set_parent_task(self._current_task)
            debug(f"scheduled task:{task.json()}")
            self._can_be_marked_as_stopped = False
            coroutine = self.send_to_queue(task, self.rabbitmq)
            ensure_future(coroutine, loop=self.loop)

        setattr(callback, "s", schedule_task)
        return schedule_task

    def task_set_redis_client(self, redis_client: RedisClient):
        """
        Set the redis client for all registered tasks
        """
        for _, runner in self.registered_tasks.items():
            runner.update_namespace(self.namespace)
            runner.set_redis_client(redis_client)
