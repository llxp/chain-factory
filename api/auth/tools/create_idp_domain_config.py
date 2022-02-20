from base64 import b64encode
from os import path
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine
from asyncio import new_event_loop

from models.idp_domain_config import IdpDomainConfig, IdpEndpointConfig

database = 'test'
mongodb_url = 'mongodb://root:example@127.0.0.1:27017/test?authSource=admin'
cert_name = 'cert.pem'
key_name = 'cert-key.pem'
domain = 'jumpcloud.com'
user_information_endpoint = \
    'https://llxp-authentication-api.herokuapp.com/user_information'
translate_users_endpoint = \
    'https://llxp-authentication-api.herokuapp.com/api/translate_users'

current_path = path.dirname(path.abspath(__file__))
pki_path = path.join(current_path, 'pki')
cert_path = path.join(pki_path, cert_name)
key_path = path.join(pki_path, key_name)

with open(cert_path, 'rb') as f:
    cert_data = f.read()
    cert_data_b64 = b64encode(cert_data).decode('utf-8')

with open(key_path, 'rb') as f:
    key_data = f.read()
    key_data_b64 = b64encode(key_data).decode('utf-8')


new_idp_config = IdpDomainConfig(
    domain=domain,
    endpoints=IdpEndpointConfig(
        user_information_endpoint=user_information_endpoint,
        translate_users_endpoint=translate_users_endpoint,
    ),
    client_certificate=cert_data_b64,
    client_certificate_key=key_data_b64
)


async def main():
    client = AsyncIOMotorClient(mongodb_url)
    engine = AIOEngine(motor_client=client, database=database)
    await engine.save(new_idp_config)

loop = new_event_loop()
loop.run_until_complete(main())
