#


### stop_node
[source](https://github.com/llxp/chain-factory/blob/master/api/routes/v1/node.py/#L38)
```python
.stop_node(
   namespace: str, node_name: str, redis_client: Redis = Depends(get_redis_client),
   database: AIOEngine = Depends(get_odm_session),
   username: str = Depends(get_username),
   namespaces: List[Namespace] = Depends(get_allowed_namespaces)
)
```


----


### node_metrics
[source](https://github.com/llxp/chain-factory/blob/master/api/routes/v1/node.py/#L83)
```python
.node_metrics(
   namespace: str, database: AIOEngine = Depends(get_odm_session),
   redis_client: Redis = Depends(get_redis_client),
   namespaces: List[str] = Depends(get_allowed_namespaces),
   username: str = Depends(get_username)
)
```


----


### delete_node
[source](https://github.com/llxp/chain-factory/blob/master/api/routes/v1/node.py/#L119)
```python
.delete_node(
   node_name: str, namespace: str, database: AIOEngine = Depends(get_odm_session),
   namespaces: List[Namespace] = Depends(get_allowed_namespaces),
   username: str = Depends(get_username)
)
```

---
Delete a node from the database.
If there are multiple nodes with the same name,
the first found node will be deleted.
If there are no nodes with the name, this will fail.


**Raises**

* **HTTPException**  : Raises exception if multiple nodes were found
* **HTTPException**  : Raises exception if node was not found
* **HTTPException**  : Raises exception if namespace not found or access denied


**Returns**

* **Str**  : Node deleted

