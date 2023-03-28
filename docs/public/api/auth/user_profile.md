#


### get_scopes_by_config
[source](https://github.com/llxp/chain-factory/blob/master/api/auth/user_profile.py/#L29)
```python
.get_scopes_by_config(
   database: AIOEngine, idp_config: IdpDomainConfig,
   user_information: UserInformation
)
```


----


### perform_user_information_request_impersonated
[source](https://github.com/llxp/chain-factory/blob/master/api/auth/user_profile.py/#L41)
```python
.perform_user_information_request_impersonated(
   idp_credentials: Credentials, user_ids: List[str], headers: dict,
   client: AsyncClient, url: str
)
```


----


### get_user_information_impersonated
[source](https://github.com/llxp/chain-factory/blob/master/api/auth/user_profile.py/#L68)
```python
.get_user_information_impersonated(
   idp_credentials: Credentials, idp_config: IdpDomainConfig, user_ids: List[str]
)
```


----


### get_user_information_by_config
[source](https://github.com/llxp/chain-factory/blob/master/api/auth/user_profile.py/#L98)
```python
.get_user_information_by_config(
   database: AIOEngine, idp_credentials: Credentials, idp_config: IdpDomainConfig,
   username: str
)
```


----


### user_profile
[source](https://github.com/llxp/chain-factory/blob/master/api/auth/user_profile.py/#L117)
```python
.user_profile(
   token: Token = Depends(get_token), database: AIOEngine = Depends(get_odm_session),
   username: str = Depends(get_username),
   idp_credentials: Credentials = Depends(get_idp_credentials)
)
```

