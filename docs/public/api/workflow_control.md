#


### stop_workflow
[source](https://github.com/llxp/chain-factory/blob/master/api/routes/v1/workflow_control.py/#L20)
```python
.stop_workflow(
   namespace: str, workflow_id: str, database: AIOEngine = Depends(get_odm_session),
   redis_client: StrictRedis = Depends(get_redis_client),
   username: str = Depends(get_username)
)
```

---
API Endpoint to stop a running workflow


**Args**

* **namespace** (str) : Namespace
* **workflow_id** (str) : ID of the selected workflow
* **database** (AIOEngine, optional) : Database Object.
    Defaults to Depends(get_odm_session).
* **redis_client** (StrictRedis, optional) : Redis Client.
    Defaults to Depends(get_redis_client).
* **username** (str, optional) : Username. Defaults to Depends(get_username).


**Raises**

* **HTTPException**  : Raises exception if workflow already stopped
* **HTTPException**  : Raises exception if namespace does not exists
    or user has no access.


**Returns**

* **Str**  : Workflow stopped


----


### abort_workflow
[source](https://github.com/llxp/chain-factory/blob/master/api/routes/v1/workflow_control.py/#L78)
```python
.abort_workflow(
   namespace: str, workflow_id: str, database: AIOEngine = Depends(get_odm_session),
   redis_client: StrictRedis = Depends(get_redis_client),
   username: str = Depends(get_username)
)
```

---
API Endpoint to abort a running workflow


**Args**

* **namespace** (str) : Namespace
* **workflow_id** (str) : ID of the selected workflow
* **database** (AIOEngine, optional) : Database Object.
    Defaults to Depends(get_odm_session).
* **redis_client** (StrictRedis, optional) : Redis Client.
    Defaults to Depends(get_redis_client).
* **username** (str, optional) : Username. Defaults to Depends(get_username).


**Raises**

* **HTTPException**  : Raises exception if workflow already stopped
* **HTTPException**  : Raises exception if namespace does not exists
    or user has no access.


**Returns**

* **Str**  : Workflow aborted


----


### restart_workflow
[source](https://github.com/llxp/chain-factory/blob/master/api/routes/v1/workflow_control.py/#L135)
```python
.restart_workflow(
   namespace: str, workflow_id: str, database: AIOEngine = Depends(get_odm_session),
   redis_client: StrictRedis = Depends(get_redis_client),
   username: str = Depends(get_username),
   rabbitmq_url: str = Depends(get_rabbitmq_url),
   namespace_obj: Namespace = Depends(get_allowed_namespace)
)
```

---
API endpoint to abort a workflow and start it again


**Args**

* **namespace** (str) : Namespace
* **workflow_id** (str) : Workflow ID
* **database** (AIOEngine, optional) : Database Object.
    Defaults to Depends(get_odm_session).
* **redis_client** (StrictRedis, optional) : Redis Client.
    Defaults to Depends(get_redis_client).
* **username** (str, optional) : Username. Defaults to Depends(get_username).
* **rabbitmq_url** (str, optional) : RabbitMQ Url.
    Defaults to Depends(get_rabbitmq_url).
* **namespace_obj** (Namespace, optional) : Namespace Object to check
if user has access to it. Defaults to Depends(get_allowed_namespace).


**Raises**

* **HTTPException**  : Raises exception if workflow could not be restarted
* **HTTPException**  : Raises exception if workflow already stopped
* **HTTPException**  : Raises exception if namespace does not exist
    or user has no access.


**Returns**

* **Str**  : Workflow restarted

