#


## ListHandler
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/wrapper/list_handler.py/#L14)
```python 
ListHandler(
   list_name: str, redis_client: RedisClient
)
```


---
Wrapper class to manage a list in redis in form of a json document


**Methods:**


### .parse_json
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/wrapper/list_handler.py/#L24)
```python
.parse_json(
   body: bytes
)
```

---
Decode the redis data to a utf-8 string,
parse the string to json and
check, if the data structure fo the parsed object is valid

### .clear
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/wrapper/list_handler.py/#L34)
```python
.clear()
```

---
Clear the redis list

### .init
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/wrapper/list_handler.py/#L44)
```python
.init()
```

---
Initialise the redis list with an empty list
if the list doesn't exist yet

### .add
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/wrapper/list_handler.py/#L55)
```python
.add(
   list_item: ListItem
)
```

---
Add an entry to the redis list

### .remove
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/wrapper/list_handler.py/#L72)
```python
.remove(
   list_item: ListItem
)
```

---
Remove an entry from the list

### .get
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/wrapper/list_handler.py/#L90)
```python
.get()
```

---
get the list
