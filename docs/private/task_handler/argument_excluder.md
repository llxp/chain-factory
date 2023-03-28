#


## ArgumentExcluder
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/argument_excluder.py/#L1)
```python 
ArgumentExcluder(
   arguments
)
```


---
This class is used to exclude arguments from the arguments dictionary,
before saving the task in the database
If the arguments dictionary contains an "exclude" key,
the values of this key will be excluded from the arguments


**Methods:**


### .exclude
[source](https://github.com/llxp/chain-factory/blob/master/framework/src/chain_factory/argument_excluder.py/#L33)
```python
.exclude()
```

---
Exclude the arguments from the arguments dictionary
