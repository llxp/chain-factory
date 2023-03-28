#


## QueueHandler
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/queue_handler.py/#L24)
```python 

```


---
Base Class for the TaskQueue,
handles the rabbitmq task queue dispatch logic


**Methods:**


### .init
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/queue_handler.py/#L32)
```python
.init(
   url: str, queue_name: str, loop: AbstractEventLoop
)
```

---
Separate init logic to be able to use lazy initialisation

### .stop_listening
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/queue_handler.py/#L39)
```python
.stop_listening()
```


### .close
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/queue_handler.py/#L43)
```python
.close()
```


### .listen
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/queue_handler.py/#L59)
```python
.listen()
```

---
starts listening on the queue

### .reschedule
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/queue_handler.py/#L67)
```python
.reschedule(
   message: Message
)
```

---
Reschedules or rather rejects the message

### ._now
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/queue_handler.py/#L74)
```python
._now()
```

---
returns the current time with timezone

### .send_to_queue
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/queue_handler.py/#L81)
```python
.send_to_queue(
   task: Task, rabbitmq: Union[RabbitMQ, None]
)
```

---
Send a task to the specified queue

### .ack
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/queue_handler.py/#L90)
```python
.ack(
   message: Message
)
```

---
Acknowledges the specified message

### .nack
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/queue_handler.py/#L98)
```python
.nack(
   message: Message
)
```

---
Rejects the specified message

### .on_task
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/queue_handler.py/#L107)
```python
.on_task(
   task: Task, message: Message
)
```

---
abstract method for the overriding clas,
will be invoked, when a new task comes in

### ._parse_json
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/queue_handler.py/#L142)
```python
._parse_json(
   body: str
)
```


### ._parse_json
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/queue_handler.py/#L142)
```python
._parse_json(
   body: str
)
```

