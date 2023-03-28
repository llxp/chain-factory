#


### login
[source](https://github.com/llxp/chain-factory/blob/master/api/auth/login.py/#L37)
```python
.login(
   request: Request, response: Response, credentials: LoginRequest,
   database: AIOEngine = Depends(get_odm_session),
   server_secret: str = Depends(get_server_secret)
)
```


----


### create_tokens
[source](https://github.com/llxp/chain-factory/blob/master/api/auth/login.py/#L78)
```python
.create_tokens(
   hostname: str, credentials: LoginRequest, server_secret: str,
   user_information: UserInformation, database: AIOEngine, response: Response
)
```

---
Creates access & refresh token,
set them as cookies and return them additionally


**Args**

* **hostname** (str) : Rest API Hostname
* **credentials** (LoginRequest) : Login POST body
    (username, password, scopes)
* **server_secret** (str) : Server secret used for jwt signage and
    jwe encryption
* **user_information** (UserInformation) : Result from authentication
    API request
* **database** (AIOEngine) : Database session (odmantic)
* **response** (Response) : FastAPI Response object


**Returns**

* **Dict**  : Access token, Refresh token


----


### get_user_information
[source](https://github.com/llxp/chain-factory/blob/master/api/auth/login.py/#L139)
```python
.get_user_information(
   credentials: Credentials, idp_config: IdpDomainConfig
)
```


----


### perform_user_information_request
[source](https://github.com/llxp/chain-factory/blob/master/api/auth/login.py/#L166)
```python
.perform_user_information_request(
   credentials: Credentials, headers: dict, client: AsyncClient, url: str
)
```


----


### get_scopes
[source](https://github.com/llxp/chain-factory/blob/master/api/auth/login.py/#L187)
```python
.get_scopes(
   scopes: List[str] = [], roles: List[IdpRoleConfig] = []
)
```


----


### create_token
[source](https://github.com/llxp/chain-factory/blob/master/api/auth/login.py/#L209)
```python
.create_token(
   hostname: str, credentials: LoginRequest, server_secret: str,
   user_information: UserInformation, username: str, database: AIOEngine, jti: str
)
```


----


### create_refresh_token
[source](https://github.com/llxp/chain-factory/blob/master/api/auth/login.py/#L231)
```python
.create_refresh_token(
   database, hostname: str, server_secret: str, user_information: UserInformation,
   credentials: LoginRequest, jti: str
)
```

