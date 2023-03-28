#


## CredentialsPool
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/credentials_pool.py/#L8)
```python 
CredentialsPool(
   endpoint: str, username: str, password: str, namespaces: Dict[str, str] = {}
)
```


---
CredentialsPool is a class that is responsible for managing the
database credentials for a specific namespace. Can be retrieved
using the credentials and the namespace key.


**Methods:**


### .init
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/credentials_pool.py/#L28)
```python
.init()
```


### .get_credentials
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/credentials_pool.py/#L33)
```python
.get_credentials(
   namespace: str, key: str = ''
)
```

---
Get the credentials for the namespace.

### .update_credentials
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/credentials_pool.py/#L50)
```python
.update_credentials()
```

---
Update the credentials internally for the namespace.
