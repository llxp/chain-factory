#


### logout
[source](https://github.com/llxp/chain-factory/blob/master/api/auth/logout.py/#L16)
```python
.logout(
   response: Response, database: AIOEngine = Depends(get_odm_session),
   token: Token = Depends(get_token)
)
```

