#


## TaskQueueHandlers
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_queue_handlers.py/#L25)
```python 
TaskQueueHandlers(
   namespace: str, namespace_key: str, node_name: str, endpoint: str, username: str,
   password: str, worker_count: int, task_timeout: int,
   loop: Optional[AbstractEventLoop] = None
)
```




**Methods:**


### .add_task
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_queue_handlers.py/#L49)
```python
.add_task(
   name: str, callback, repeat_on_timeout: bool = False
)
```


### .add_error_handler
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_queue_handlers.py/#L52)
```python
.add_error_handler(
   exc_type, callback: ErrorCallbackType
)
```


### .namespaced
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_queue_handlers.py/#L55)
```python
.namespaced(
   var: str
)
```


### .task_queue
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_queue_handlers.py/#L61)
```python
.task_queue()
```


### .incoming_blocked_queue
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_queue_handlers.py/#L65)
```python
.incoming_blocked_queue()
```


### .wait_queue
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_queue_handlers.py/#L69)
```python
.wait_queue()
```


### .redis_client
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_queue_handlers.py/#L72)
```python
.redis_client()
```


### .mongodb_client
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_queue_handlers.py/#L76)
```python
.mongodb_client()
```


### .init
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_queue_handlers.py/#L79)
```python
.init()
```

---
Init all handlers
-> wait handler
-> incoming blocked handler
-> wait blocked handler
-> task handler
-> cluster heartbeat

### .listen
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_queue_handlers.py/#L139)
```python
.listen()
```

---
Initialises the queue and starts listening

### .stop_heartbeat
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_queue_handlers.py/#L152)
```python
.stop_heartbeat()
```


### .stop_node
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_queue_handlers.py/#L157)
```python
.stop_node()
```


### .count_running_tasks
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_queue_handlers.py/#L175)
```python
.count_running_tasks()
```


### .stop_listening
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_queue_handlers.py/#L194)
```python
.stop_listening()
```

