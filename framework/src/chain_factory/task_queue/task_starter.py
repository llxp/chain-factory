from .models.mongodb_models import Task
from .wrapper.rabbitmq import RabbitMQ, getPublisher


class TaskStarter:
    def __init__(
        self,
        namespace: str,
        rabbitmq_url: str,
    ):
        self.namespace = namespace
        queue_name = namespace + "_task_queue"
        self.amqp_client: RabbitMQ = getPublisher(rabbitmq_url=rabbitmq_url, queue_name=queue_name)  # noqa: E501

    async def start_task(self, task_name, arguments, node_names=[], tags=[]):
        task = Task(name=task_name, arguments=arguments, node_names=node_names, tags=tags)  # noqa: E501
        task_json = task.json()
        await self.amqp_client.send(task_json)
