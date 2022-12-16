from logging import basicConfig, DEBUG
from os import getenv
from time import sleep
from pathlib import Path
from sys import path
from framework.src.chain_factory.task_queue.models.mongodb_models import Task
from framework.src.chain_factory.task_queue.task_queue import TaskQueue
path.append(Path(
    __file__).parent.parent.absolute().as_posix() + '/src')

# import hanging_threads

FORMAT = (
    '%(asctime)s.%(msecs)03d %(levelname)8s: '
    '[%(pathname)10s:%(lineno)s - '
    '%(funcName)20s() ] %(message)s'
)
basicConfig(
    filename='logfile.log',
    level=DEBUG,
    format=FORMAT,
    datefmt='%Y-%m-%d %H:%M:%S'
)

# create the main TaskQueue object
task_queue = TaskQueue()
host = '127.0.0.1'
# the current node name. Should be later changed to an environment variable
task_queue.node_name = getenv('HOSTNAME', 'devnode01')
# the amqp endpoint. Should later be changed to an environment variable
task_queue.amqp_host = getenv('RABBITMQ_HOST', host)
# the redis endpoint. Should later be changed to an environment variable
task_queue.redis_host = getenv('REDIS_HOST', host)
# the amqp username ==> guest is the default
task_queue.amqp_username = getenv('RABBITMQ_USER', 'guest')
# the amqp passwort ==> guest is the default
task_queue.amqp_password = getenv('RABBITMQ_PASSWORD', 'guest')
task_queue.mongodb_connection = getenv(
    'MONGODB_CONNECTION_URI',
    'mongodb://root:example@' + host + '/orchestrator_db?authSource=admin'
)
task_queue.worker_count = 10
task_queue.namespace = "root"

counter = 0


@task_queue.task()
def test01(testvar01: int):
    print(testvar01)
    print("Hello World!")


@task_queue.task()
def test02():
    print('Test02<s>SECRET</s>')
    raise TypeError
    return 'test01', {'testvar01': '01'}


@task_queue.task('simulate')
def simulate(times: int, i: int, exclude=['i']):
    print(" [x] Received simulate task")
    # print('times: ' + str(times))
    # print('i' + str(i))
    global counter
    counter = counter + 1
    print('counter: ' + str(counter))
    print(type(times))
    # for i in range(0, times):
    # sleep(times)
    print(" [x] Done %d" % i)
    for x in range(0, times):
        print(x)
        sleep(1)
    return None


@task_queue.task('test_task')
def test_task():
    print("test task")
    print('Test02<s>SECRET</s>')
    return 'simulate', {'i': 0, 'times': 30}


@task_queue.task('send_feedback')
def send_feedback(feedback):
    print('feedback: %s' % (feedback, ))
    return None


@task_queue.task()
def workflow_task():
    print('schedule next task: send_feedback')
    return Task(name='send_feedback', arguments={'feedback': 'success'})


@task_queue.task()
def failed_task(failed_counter: int):
    print('Error, task failed!')
    failed_counter = failed_counter + 1
    if failed_counter >= 3:
        return None
    return False, {'failed_counter': failed_counter}


@task_queue.task()
def chained_task_01():
    print('chained_task_01')
    return Task('chained_task_02', {'arg1': 'test01'})


@task_queue.task()
def chained_task_02(arg1: str = 'test02'):
    print('chained_task_02')
    print('arg1_chained_task_02: ' + arg1)
    if arg1 == 'test01':
        print('...')
        return 'chained_task_03', {'arg2': 'test'}
    else:
        return None


@task_queue.task()
def chained_task_03(arg2: str):
    print('chained_task_03')
    return chained_task_02, {'arg1': 'test02'}


if __name__ == '__main__':
    task_queue.listen()  # start the node

    # sleep(1000)
    task_queue.run_main_loop()
