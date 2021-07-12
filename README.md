# chain-factory
Chain Factory master repository of the Chain Factory project

A framework to dispatch tasks fetched from an amqp queue to several worker nodes

## How to use

### components
 - Redis
 - RabbitMQ
 - backend_api
 - admin_ui (angular frontend)
 - worker node

## Development environment to develop the workflows

### Backend
start the dev backend using the prepared docker-compose file

    cd docker
    ./prepare_build.sh
    docker-compose build
    ./cleanup_build.sh
    docker-compose up -d

### worker node
To start a worker node you need to install the dependencies first and adjust the settings to point to the correct rabbitmq and redis server

    pip install -r requirements.txt
    # then start the worker node using
    python ./main.py

If you are on a system with both python2 and python3 installed, you need to specify python3 instead of python as python on most systems is sym-linked with python2


## How to register new tasks to the worker node
To register new tasks to the worker node add either a new function together with the decorator

    @task_queue.task()
    def new_task():
        print('example')

Or register the task using the decorator and using an imported function in an external file e.g.

    # file1.py
    class ExampleClass():
        def example_task(self):
            print('example')
   
    # main.py
    from file1 import ExampleClass
    example_instance = ExampleClass()
    task_queue.task('example_task')(example_instance.example_task)
