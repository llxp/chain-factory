#


### new_task
[source](https://github.com/llxp/chain-factory/blob/master/api/routes/v1/task_control.py/#L30)
```python
.new_task(
   namespace: str, task_name: str, json_body: NewTaskRequest = Body(...),
   username: str = Depends(get_username),
   rabbitmq_url: str = Depends(get_rabbitmq_url),
   database: AIOEngine = Depends(get_odm_session)
)
```

