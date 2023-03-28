#


## TaskHandler
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_handler.py/#L51)
```python 
TaskHandler(
   namespace: str, node_name: str
)
```




**Methods:**


### .init
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_handler.py/#L66)
```python
.init(
   mongodb_client: AIOEngine, redis_client: RedisClient, queue_name: str,
   wait_queue_name: str, blocked_queue_name: str, loop: AbstractEventLoop,
   rabbitmq_url: str
)
```

---
Initialize the task handler
there is this extra init function, because the __init__ function
does not support async functions

### .update_task_timeout
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_handler.py/#L108)
```python
.update_task_timeout()
```

---
Update the task timeout value for all registered tasks

### .update_error_handlers
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_handler.py/#L115)
```python
.update_error_handlers()
```

---
Update the error handlers for all registered tasks

### .check_rejected_task
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_handler.py/#L574)
```python
.check_rejected_task(
   task: Task, message: Message
)
```

---
Checks if the task has been rejected too often

### .on_task
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_handler.py/#L584)
```python
.on_task(
   task: Task, message: Message
)
```

---
The callback function, which will be called from the rabbitmq library
It deserializes the amqp message and then
checks, if the requested taks is registered and calls it.
If the task name is on the blocklist,
it will be rejected, rescheduled and then wait for some time

Returns either None or a new task

### .add_task
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_handler.py/#L617)
```python
.add_task(
   name: str, callback: CallbackType, repeat_on_timeout: bool
)
```

---
Register a new task/task function

### .add_error_handler
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_handler.py/#L627)
```python
.add_error_handler(
   exc_type: Type[Exception], callback: ErrorCallbackType
)
```

---
Register a new error handler

:param callback: the callback function
:type callback: Callable[[Task, Exception], None]

### .clear_error_handlers
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_handler.py/#L637)
```python
.clear_error_handlers()
```

---
Clear all registered error handlers

### .add_schedule_task_shortcut
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_handler.py/#L644)
```python
.add_schedule_task_shortcut(
   name: str, callback: CallbackType
)
```

---
Add a function to the registered function named .s()
to schedule the function with or without arguments

### .task_set_redis_client
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_handler.py/#L671)
```python
.task_set_redis_client(
   redis_client: RedisClient
)
```

---
Set the redis client for all registered tasks
