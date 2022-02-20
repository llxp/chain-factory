from os import getenv

from framework.src.chain_factory.task_queue import TaskQueue


app = TaskQueue(
    endpoint='http://127.0.0.1:8005',
    username='llxp@jumpcloud.com',
    password='WmNNJPf7wTurU9t',
    namespace='root',
    namespace_key='root',
)
host = '127.0.0.1'
# the current node name. Should be later changed to an environment variable
app.node_name = getenv('HOSTNAME', 'devnode01')
# the amqp endpoint. Should later be changed to an environment variable
app.amqp_host = getenv('RABBITMQ_HOST', host)
# the redis endpoint. Should later be changed to an environment variable
app.redis_host = getenv('REDIS_HOST', host)
# the amqp username ==> guest is the default
app.amqp_username = getenv('RABBITMQ_USER', 'guest')
# the amqp passwort ==> guest is the default
app.amqp_password = getenv('RABBITMQ_PASSWORD', 'guest')
app.mongodb_connection = getenv(
    'MONGODB_CONNECTION_URI',
    'mongodb://root:example@' + host + '/orchestrator_db?authSource=admin'
)
app.worker_count = 10
app.namespace = "root"


@app.task()
async def test01(testvar01: int):
    print(testvar01)
    print("Hello World!")
