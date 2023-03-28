#


### workflows
[source](https://github.com/llxp/chain-factory/blob/master/api/routes/v1/workflow.py/#L27)
```python
.workflows(
   namespace: str,
   namespaces: List[str] = Depends(get_allowed_namespaces_even_disabled),
   database: AIOEngine = Depends(get_odm_session),
   username: str = Depends(get_username), search: str = '', page: int = -1,
   page_size: int = -1, sort_by: str = '', sort_order: str = '', begin: str = '',
   end: str = ''
)
```


----


### workflow_tasks
[source](https://github.com/llxp/chain-factory/blob/master/api/routes/v1/workflow.py/#L273)
```python
.workflow_tasks(
   workflow_id: str, namespace: str, database: AIOEngine = Depends(get_odm_session),
   username: str = Depends(get_username), page: int = -1, page_size: int = -1
)
```


----


### workflow_status
[source](https://github.com/llxp/chain-factory/blob/master/api/routes/v1/workflow.py/#L313)
```python
.workflow_status(
   namespace: str, database: AIOEngine = Depends(get_odm_session),
   namespaces: List[str] = Depends(get_allowed_namespaces_even_disabled),
   workflow_id: List[str] = Query([]), username: str = Depends(get_username)
)
```


----


### workflow_metrics
[source](https://github.com/llxp/chain-factory/blob/master/api/routes/v1/workflow.py/#L407)
```python
.workflow_metrics(
   namespace: str, database: AIOEngine = Depends(get_odm_session),
   namespaces: List[str] = Depends(get_allowed_namespaces_even_disabled),
   username: str = Depends(get_username)
)
```


----


### delete_workflow_logs
[source](https://github.com/llxp/chain-factory/blob/master/api/routes/v1/workflow.py/#L456)
```python
.delete_workflow_logs(
   workflow_id: str, force: bool = Query(False),
   database: AIOEngine = Depends(get_odm_session),
   username: str = Depends(get_username)
)
```


----


### workflow_logs
[source](https://github.com/llxp/chain-factory/blob/master/api/routes/v1/workflow.py/#L517)
```python
.workflow_logs(
   workflow_id: str, database: AIOEngine = Depends(get_odm_session), page: int = -1,
   page_size: int = -1, namespaces: List[str] = Depends(get_allowed_namespaces),
   username: str = Depends(get_username)
)
```

