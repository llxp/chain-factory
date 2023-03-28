#


### parse_catcher
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/decorators/parse_catcher.py/#L8)
```python
.parse_catcher(
   errors: Tuple[Type[Exception], ...] = (Exception, )
)
```

---
Catches exceptions and prints them to stdout.
Returns None if an exception is caught
Used in QueueHandler and ListHandler
