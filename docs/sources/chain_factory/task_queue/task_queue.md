#


## TaskQueue
[source](https://github.com/llxp/chain-factory\blob\master\framework/src/chain_factory/task_queue/task_queue.py\#L17)
```python 
TaskQueue(
   endpoint: str, username: str, password: str, namespace: str = default_namespace,
   namespace_key: str = default_namespace_key,
   worker_count: int = default_worker_count, task_timeout: int = default_task_timeout,
   task_repeat_on_timeout: bool = default_task_repeat_on_timeout,
   node_name: str = generate_random_id()
)
```


---
Main Class for the chain-factory framework


**Methods:**


### .start_new_task
[source](https://github.com/llxp/chain-factory\blob\master\framework/src/chain_factory/task_queue/task_queue.py\#L59)
```python
.start_new_task(
   task_name: str, arguments: dict, namespace: str = None, namespace_key: str = None
)
```

---
starts a new task

### .wait_for_task
[source](https://github.com/llxp/chain-factory\blob\master\framework/src/chain_factory/task_queue/task_queue.py\#L88)
```python
.wait_for_task(
   namespace: str, task_name: str, arguments: dict
)
```

---
waits for a task to complete

### .task
[source](https://github.com/llxp/chain-factory\blob\master\framework/src/chain_factory/task_queue/task_queue.py\#L99)
```python
.task(
   name: str = '', repeat_on_timeout: bool = default_task_repeat_on_timeout
)
```

---
Decorator to register a new task in the framework

- Registers a new task in the framework internally
- using the function name as the task name
- using the function as the task handler, which will be wrapped internally in a TaskRunner class
---
- also adds a special `.s` method to the function, which can be used to start the function as a task from inside another task (for chaining of tasks)
- registration in mongodb will be done during the initialisation phase

### .add_task
[source](https://github.com/llxp/chain-factory\blob\master\framework/src/chain_factory/task_queue/task_queue.py\#L125)
```python
.add_task(
   func, name: str = '', repeat_on_timeout: bool = default_task_repeat_on_timeout
)
```

---
Method to add tasks, which cannot be added using the decorator

- Calls the `task` decorator

### .listen
[source](https://github.com/llxp/chain-factory\blob\master\framework/src/chain_factory/task_queue/task_queue.py\#L139)
```python
.listen(
   loop: AbstractEventLoop = None
)
```

---
Initialises the queue and starts listening

### .run
[source](https://github.com/llxp/chain-factory\blob\master\framework/src/chain_factory/task_queue/task_queue.py\#L159)
```python
.run()
```

---
Runs the task queue:

- Starts the event loop
- Starts listening for tasks
- and stops the event loop on keyboard interrupt
