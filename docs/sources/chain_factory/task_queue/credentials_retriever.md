#


## CredentialsRetriever
[source](https://github.com/llxp/chain-factory\blob\master\framework/src/chain_factory/task_queue/credentials_retriever.py\#L8)
```python 
CredentialsRetriever(
   endpoint: str, namespace: str, username: str, password: str, key: str
)
```


---
Retrieve database credentials from rest api


**Methods:**


### .init
[source](https://github.com/llxp/chain-factory\blob\master\framework/src/chain_factory/task_queue/credentials_retriever.py\#L36)
```python
.init()
```

---
The init method is used to initialize the class as the `__init__` method does not work with async

### .mongodb
[source](https://github.com/llxp/chain-factory\blob\master\framework/src/chain_factory/task_queue/credentials_retriever.py\#L52)
```python
.mongodb()
```

---
get MongoDB credentials from credentials

### .redis
[source](https://github.com/llxp/chain-factory\blob\master\framework/src/chain_factory/task_queue/credentials_retriever.py\#L57)
```python
.redis()
```

---
get redis credentials from credentials

### .redis_prefix
[source](https://github.com/llxp/chain-factory\blob\master\framework/src/chain_factory/task_queue/credentials_retriever.py\#L62)
```python
.redis_prefix()
```

---
get redis prefix from credentials

### .rabbitmq
[source](https://github.com/llxp/chain-factory\blob\master\framework/src/chain_factory/task_queue/credentials_retriever.py\#L67)
```python
.rabbitmq()
```

---
get rabbitmq credentials from credentials

### .get_jwe_token
[source](https://github.com/llxp/chain-factory\blob\master\framework/src/chain_factory/task_queue/credentials_retriever.py\#L71)
```python
.get_jwe_token(
   username, password
)
```

---
send login request to internal rest-api on /api/login

### .get_credentials
[source](https://github.com/llxp/chain-factory\blob\master\framework/src/chain_factory/task_queue/credentials_retriever.py\#L87)
```python
.get_credentials()
```

---
retrieve namespace credentials from internal rest-api on /api/v1/credentials
using login token and namespace/namespace-key (which is used to decrypt the credentials created on namespace key rotation)
