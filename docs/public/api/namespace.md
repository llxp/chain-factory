#


### namespaces
[source](https://github.com/llxp/chain-factory/blob/master/api/routes/v1/namespace.py/#L19)
```python
.namespaces(
   database: AIOEngine = Depends(get_odm_session),
   username: str = Depends(get_username)
)
```


----


### disabled_namespaces
[source](https://github.com/llxp/chain-factory/blob/master/api/routes/v1/namespace.py/#L33)
```python
.disabled_namespaces(
   database: AIOEngine = Depends(get_odm_session),
   username: str = Depends(get_username)
)
```


----


### create_namespace
[source](https://github.com/llxp/chain-factory/blob/master/api/routes/v1/namespace.py/#L47)
```python
.create_namespace(
   namespace: str, database: AIOEngine = Depends(get_odm_session),
   username: str = Depends(get_username),
   breakglass_username: str = Depends(get_breakglass_username),
   breakglass_domain: str = Depends(get_breakglass_domain)
)
```


----


### allow_user_to_namespace
[source](https://github.com/llxp/chain-factory/blob/master/api/routes/v1/namespace.py/#L86)
```python
.allow_user_to_namespace(
   namespace: str, username: str, current_user: str = Depends(get_username),
   database: AIOEngine = Depends(get_odm_session)
)
```


----


### remove_user_from_namespace
[source](https://github.com/llxp/chain-factory/blob/master/api/routes/v1/namespace.py/#L109)
```python
.remove_user_from_namespace(
   namespace: str, username: str, current_user: str = Depends(get_username),
   database: AIOEngine = Depends(get_odm_session)
)
```


----


### disable_namespace
[source](https://github.com/llxp/chain-factory/blob/master/api/routes/v1/namespace.py/#L129)
```python
.disable_namespace(
   namespace: str, username: str = Depends(get_username),
   database: AIOEngine = Depends(get_odm_session)
)
```


----


### delete_namespace
[source](https://github.com/llxp/chain-factory/blob/master/api/routes/v1/namespace.py/#L144)
```python
.delete_namespace(
   namespace: str, username: str = Depends(get_username),
   database: AIOEngine = Depends(get_odm_session),
   redis_client: Redis = Depends(get_redis_client),
   rabbitmq_management_api: ManagementApi = Depends(get_rabbitmq_management_api)
)
```


----


### enable_namespace
[source](https://github.com/llxp/chain-factory/blob/master/api/routes/v1/namespace.py/#L193)
```python
.enable_namespace(
   namespace: str, username: str = Depends(get_username),
   database: AIOEngine = Depends(get_odm_session)
)
```


----


### rename_namespace
[source](https://github.com/llxp/chain-factory/blob/master/api/routes/v1/namespace.py/#L208)
```python
.rename_namespace(
   namespace: str, new_namespace: str, username: str = Depends(get_username),
   database: AIOEngine = Depends(get_odm_session)
)
```

