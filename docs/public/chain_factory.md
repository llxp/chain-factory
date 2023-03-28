#


## ChainFactory
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/chain_factory.py/#L27)
```python 
ChainFactory(
   endpoint: str, username: str, password: str, node_name: str,
   namespace: str = default_namespace, namespace_key: str = default_namespace_key,
   worker_count: int = default_worker_count, task_timeout: int = default_task_timeout,
   task_repeat_on_timeout: bool = default_task_repeat_on_timeout
)
```


---
Main Class for the chain-factory framework

This class is used
to initialize the framework by creating a new instance of the class
to register tasks and
to start listening


**Methods:**


### .task
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/chain_factory.py/#L73)
```python
.task(
   name: str = '', repeat_on_timeout: bool = default_task_repeat_on_timeout
)
```

---
Decorator to register a new task in the framework

- Registers a new task in the framework internally
- using the function name as the task name
- using the function as the task handler,
  which will be wrapped internally in a TaskRunner class
---
- also adds a special `.s` method to the function,
  which can be used to start the function as a task
  from inside another task (for chaining of tasks)
- registration in mongodb will be done during the initialisation phase

### .add_task
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/chain_factory.py/#L97)
```python
.add_task(
   func, name: str = '', repeat_on_timeout: bool = default_task_repeat_on_timeout
)
```

---
Method to add tasks, which cannot be added using the decorator

- Calls the `task` decorator

### .add_error_context
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/chain_factory.py/#L111)
```python
.add_error_context()
```

---
Decorator to add workflow context to a task

- Adds the workflow context to the task

### .shutdown
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/chain_factory.py/#L124)
```python
.shutdown()
```

---
Shuts down the framework

### .add_error_handler
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/chain_factory.py/#L131)
```python
.add_error_handler(
   exc_type: Type[Exception], func: ErrorCallbackType
)
```

---
Adds an error handler to the framework

### .listen
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/chain_factory.py/#L137)
```python
.listen(
   loop: Optional[AbstractEventLoop] = None
)
```

---
Initialises the queue and starts listening

- Will be invoked by the `run` method

### .run
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/chain_factory.py/#L178)
```python
.run(
   loop: Optional[AbstractEventLoop] = None
)
```

---
Runs the task queue:

- Starts a new event loop or uses a provided one
- Starts listening for tasks
- and stops the event loop on keyboard interrupt
