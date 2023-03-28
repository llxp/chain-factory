#


## ClientPool
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/client_pool.py/#L19)
```python 

```




**Methods:**


### .init
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/client_pool.py/#L28)
```python
.init(
   redis_url: str, key_prefix: str, mongodb_url: str, loop: AbstractEventLoop
)
```

---
- initialises the redis client
- initialises the mongodb client

### .redis_client
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/client_pool.py/#L43)
```python
.redis_client(
   redis_url: str = 'default', key_prefix: str = '',
   loop: Optional[AbstractEventLoop] = None
)
```

---
return a redis client specific to the given redis url
if no redis url is given, return the default redis client
if no default redis client exists,
create a new one with the given redis url

### .close
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/client_pool.py/#L113)
```python
.close()
```

---
closes all the clients
