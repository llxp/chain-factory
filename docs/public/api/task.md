#


### active_tasks
[source](https://github.com/llxp/chain-factory/blob/master/api/routes/v1/task.py/#L26)
```python
.active_tasks(
   namespace: str, database: AIOEngine = Depends(get_odm_session),
   redis_client: Redis = Depends(get_redis_client),
   username: str = Depends(get_username), search: str = '', page: int = -1,
   page_size: int = -1
)
```


----


### tasks
[source](https://github.com/llxp/chain-factory/blob/master/api/routes/v1/task.py/#L75)
```python
.tasks(
   namespace: str, username: str, search: str, database: AIOEngine, page: int = -1,
   page_size: int = -1, nodes: List[NodeTasks] = []
)
```


----


### task_logs
[source](https://github.com/llxp/chain-factory/blob/master/api/routes/v1/task.py/#L158)
```python
.task_logs(
   task_id: str, namespace: str,
   namespaces: List[str] = Depends(get_allowed_namespaces),
   username: str = Depends(get_username), page: int = -1, page_size: int = -1,
   database: AIOEngine = Depends(get_odm_session)
)
```

