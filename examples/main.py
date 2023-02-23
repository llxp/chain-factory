from logging import Formatter, StreamHandler, basicConfig, getLogger
from os import getenv
from sys import stdout
from time import sleep
from chain_factory.models.mongodb_models import Task
from framework.src.chain_factory import ChainFactory

# environment variables
logging_level: str = getenv("LOG_LEVEL", "DEBUG")
cf_username: str = getenv('CHAIN_FACTORY_USERNAME', 'admin')
cf_password: str = getenv('CHAIN_FACTORY_PASSWORD', 'admin')
cf_endpoint: str = getenv('CHAIN_FACTORY_ENDPOINT', 'http://localhost:8005')
cf_namespace: str = getenv('CHAIN_FACTORY_NAMESPACE', 'test01')
# the namespace key can be retrieved through the chain-factory web interface
# select a namespace
#   -> edit
#   -> rotate key
#   -> the new key will appear
#   -> copy it (the key will disappear when closing the modal)
cf_namespace_key: str = getenv('CHAIN_FACTORY_NAMESPACE_KEY', '...')
node_name = getenv('HOSTNAME', 'devnode01')

# the default logging format
logging_fmt = "%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s"  # noqa: E501
try:
    root_logger = getLogger()
    root_logger.setLevel(logging_level)
    root_handler = StreamHandler(stdout)
    root_logger.addHandler(root_handler)
    root_handler.setFormatter(Formatter(logging_fmt))
except IndexError:
    basicConfig(level=logging_level, format=logging_fmt)

# create the main TaskQueue object
task_queue = ChainFactory(
    username=cf_username,
    password=cf_password,
    endpoint=cf_endpoint,
    namespace=cf_namespace,
    namespace_key=cf_namespace_key,
    node_name=node_name
)
task_queue.worker_count = 10


@task_queue.task()
def test01(testvar01: int):
    print(testvar01)
    print("Hello World!")


@task_queue.task()
def test02():
    print('Test02<s>SECRET</s>')
    raise TypeError
    return test01.s(testvar01='01')  # a next task can be started using the .s() method, this is the preferred way  # noqa: E501


counter = 0


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
    return None  # can also be ommitted


@task_queue.task('test_task')
def test_task():
    print("test task")
    print('Test02<s>SECRET</s>')
    return 'simulate', {'i': 0, 'times': 30}  # a task can also be returned by name  # noqa: E501


@task_queue.task('send_feedback')
def send_feedback(feedback):
    print('feedback: %s' % (feedback, ))
    return None


@task_queue.task()
def workflow_task():
    print('schedule next task: send_feedback')
    return Task(name='send_feedback', arguments={'feedback': 'success'})  # a task can also be returned by Task object  # noqa: E501


@task_queue.task()
def failed_task(failed_counter: int):
    print('Error, task failed!')
    failed_counter = failed_counter + 1
    if failed_counter >= 3:
        return None
    return False, {'failed_counter': failed_counter}  # when returning False, the task will be retried  # noqa: E501


# an example of a chained task

@task_queue.task()
def chained_task_01():
    print('chained_task_01')
    return 'chained_task_02', {'arg1': 'test01'}


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
    task_queue.run()
