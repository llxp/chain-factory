#


## TaskControlThread
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_control_thread.py/#L14)
```python 
TaskControlThread(
   workflow_id: str, task_thread: TaskThread, redis_client: RedisClient,
   namespace: str
)
```


---
TaskControlThread is a thread that listens to a redis channel for control
messages. It is used to stop or abort a task.
ControlThread is a base class that is used to implement the redis broadcast
listener.
