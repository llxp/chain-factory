#


## ControlThread
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/control_thread.py/#L21)
```python 
ControlThread(
   workflow_id: str, control_actions: Dict[str, Callable],
   redis_client: RedisClient, control_channel: str, thread_name: str = ''
)
```


---
The thread which handles the control messages
Can be interrupted by calling stop()


**Methods:**


### .stop
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/control_thread.py/#L42)
```python
.stop()
```


### .run_async
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/control_thread.py/#L52)
```python
.run_async(
   loop: Optional[AbstractEventLoop] = None
)
```

