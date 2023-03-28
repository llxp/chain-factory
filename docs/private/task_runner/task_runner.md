#


## TaskRunner
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_runner.py/#L33)
```python 
TaskRunner(
   name: str, callback: CallbackType, namespace: str
)
```




**Methods:**


### .set_redis_client
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_runner.py/#L50)
```python
.set_redis_client(
   redis_client: RedisClient
)
```


### .update_task_timeout
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_runner.py/#L53)
```python
.update_task_timeout(
   task_timeout: int
)
```


### .update_error_handlers
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_runner.py/#L56)
```python
.update_error_handlers(
   error_handlers: ErrorCallbackMappingType
)
```


### .update_task_repeat_on_timeout
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_runner.py/#L60)
```python
.update_task_repeat_on_timeout(
   task_repeat_on_timeout: bool
)
```


### .task_repeat_on_timeout
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_runner.py/#L64)
```python
.task_repeat_on_timeout()
```


### .update_namespace
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_runner.py/#L67)
```python
.update_namespace(
   namespace: str
)
```


### .running_workflows
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_runner.py/#L70)
```python
.running_workflows()
```


### .run
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_runner.py/#L73)
```python
.run(
   workflow: Optional[Workflow], task: Task, buffer: BytesIO,
   loop: Optional[AbstractEventLoop] = get_event_loop()
)
```


### ._parse_task_output
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_runner.py/#L159)
```python
._parse_task_output(
   task_result: FreeTaskReturnType, old_arguments: ArgumentType
)
```

---
Check, if new parameters have been returned,
to be able to reschedule the same task with changed parameters
Returns the result of the task and the arguments,
either the default arguments or the newly returned arguments

### .convert_arguments
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_runner.py/#L191)
```python
.convert_arguments(
   arguments: ArgumentType
)
```


### .abort
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_runner.py/#L205)
```python
.abort(
   workflow_id: str
)
```


### .stop
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/task_runner.py/#L209)
```python
.stop(
   workflow_id: str
)
```

