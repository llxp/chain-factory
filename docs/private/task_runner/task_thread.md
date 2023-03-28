#


## TaskThread
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_thread.py/#L26)
```python 
TaskThread(
   name: str, callback: Callable, arguments, buffer: BytesIO,
   error_handlers: ErrorCallbackMappingType, workflow: Optional[Workflow],
   task: Task
)
```


---
The thread which actually runs the task
the output of stdio will be redirected to a buffer
and later uploaded to the mongodb database


**Methods:**


### .run
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_thread.py/#L74)
```python
.run()
```


### .try_error_handler
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_thread.py/#L112)
```python
.try_error_handler(
   e
)
```


### .stop
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_thread.py/#L136)
```python
.stop()
```


### .abort
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_thread.py/#L142)
```python
.abort()
```


### .abort_timeout
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_thread.py/#L148)
```python
.abort_timeout()
```

