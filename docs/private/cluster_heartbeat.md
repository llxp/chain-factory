#


## ClusterHeartbeat
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/cluster_heartbeat.py/#L20)
```python 
ClusterHeartbeat(
   namespace: str, node_name: str, client_pool: ClientPool, loop: AbstractEventLoop
)
```




**Methods:**


### .start_heartbeat
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/cluster_heartbeat.py/#L35)
```python
.start_heartbeat()
```

---
starts the heartbeat thread

### .stop_heartbeat
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/cluster_heartbeat.py/#L42)
```python
.stop_heartbeat()
```

---
stops the heartbeat thread
