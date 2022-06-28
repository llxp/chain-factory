from os import path
from typing import Tuple
from urllib import parse

from .base64 import decode_write_b64
from .files import file_exists

from ..models.idp_domain_config import IdpClientCertConfig, IdpDomainConfig


async def get_cert_paths(domain: str):
    current_path = path.dirname(path.realpath(__file__))
    pki_path = path.join(current_path, 'pki')
    cert_path = path.join(pki_path, domain + '.crt')
    key_path = path.join(pki_path, domain + '.key')
    return cert_path, key_path


async def get_client_certificates(
    domain: str,
    client_cert_config: IdpClientCertConfig
) -> Tuple[str, str]:
    """
    check, if the certificate for the given url is already downloaded
    download the certificate if not already downloaded
    return certificate_path and key_path
    """
    # check if the certificate is already downloaded
    cert_path, key_path = await get_cert_paths(domain)
    if await file_exists(cert_path) and await file_exists(key_path):
        return cert_path, key_path
    cert_data_b64 = client_cert_config.cert
    key_data_b64 = client_cert_config.key
    await decode_write_b64(cert_path, cert_data_b64)
    await decode_write_b64(key_path, key_data_b64)
    return cert_path, key_path


async def get_ca_server_certificates():
    current_path = path.dirname(path.realpath(__file__))
    pki_path = path.join(current_path, 'pki')
    ca_path = path.join(pki_path, 'ca.pem')
    if await file_exists(ca_path):
        return ca_path
    return None

def is_https(url: str):
    parsed_url = parse.urlparse(url)
    return parsed_url.scheme == 'https' or not parsed_url.scheme == 'http'


async def get_https_certificates(url: str, config: IdpDomainConfig):
    if url and is_https(url):
        return await get_client_certificates(
            config.domain, config.client_cert_config)
    return None

async def get_ca_certificates(url: str):
    if url and is_https(url):
        return await get_ca_server_certificates()
    return False