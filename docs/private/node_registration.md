#


## NodeRegistration
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/node_registration.py/#L21)
```python 
NodeRegistration(
   namespace: str, database: AIOEngine, node_name: str, task_handler: TaskHandler
)
```




**Methods:**


### .register_tasks
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/node_registration.py/#L34)
```python
.register_tasks()
```

---
Registers all internally registered tasks in the database
in the form:
node_name/task_name

### .register
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/node_registration.py/#L109)
```python
.register()
```

