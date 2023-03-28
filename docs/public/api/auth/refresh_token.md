#


### access_token_from_refresh_token
[source](https://github.com/llxp/chain-factory/blob/master/api/auth/refresh_token.py/#L18)
```python
.access_token_from_refresh_token(
   bearer_token: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
   server_secret: str = Depends(get_server_secret),
   database: AIOEngine = Depends(get_odm_session),
   hostname: str = Depends(get_hostname)
)
```


----


### create_token
[source](https://github.com/llxp/chain-factory/blob/master/api/auth/refresh_token.py/#L39)
```python
.create_token(
   database: AIOEngine, token: CredentialsToken, hostname: str, key: str
)
```


----


### find_refresh_token
[source](https://github.com/llxp/chain-factory/blob/master/api/auth/refresh_token.py/#L61)
```python
.find_refresh_token(
   database: AIOEngine, jti: str
)
```

