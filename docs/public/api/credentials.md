#


### create_credentials
[source](https://github.com/llxp/chain-factory/blob/master/api/routes/v1/credentials.py/#L42)
```python
.create_credentials(
   namespace: str, database: AIOEngine = Depends(get_odm_session),
   username: str = Depends(get_username),
   redis_client: Redis = Depends(get_redis_client),
   rabbitmq_management_api: ManagementApi = Depends(get_rabbitmq_management_api),
   namespace_obj: Namespace = Depends(get_allowed_namespace)
)
```

---
Create credentials for a namespace.
Encrypt the credentials and
return the password to retrieve the credentials.
Return an error if the namespace does not exist


**Raises**

* **HTTPException**  : Raises exception if credentials could not be created
* **HTTPException**  : Raises exception if namespace does not exist or user
    has no access


**Returns**

ManagementCredentials(Object)

----


### get_credentials
[source](https://github.com/llxp/chain-factory/blob/master/api/routes/v1/credentials.py/#L99)
```python
.get_credentials(
   namespace: str, key: str, database: AIOEngine = Depends(get_odm_session)
)
```

---
Get credentials for the current user.
1. check, if the current user has access to the requested namespace
2. check, if the credentials are already stored in the database
3. if not, create new credentials and store them in the database
4. the credentials are only valid a limited amount of time
5. return the credentials
