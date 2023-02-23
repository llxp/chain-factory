from logging import debug
from os import getenv, path
from ssl import CERT_NONE, CERT_REQUIRED, PROTOCOL_TLS, SSLContext
from typing import Literal, Tuple, Union
from urllib import parse

from .base64 import decode_write_b64
from .files import file_exists

from ..models.idp_domain_config import IdpClientCertConfig, IdpDomainConfig


async def get_cert_paths(domain: str):
    normalized_domain = domain.replace('.', '_').replace(':', '_')
    debug(f"get_cert_paths: {domain} {normalized_domain}")
    current_path = path.dirname(path.realpath(__file__))
    pki_path = path.join(current_path, 'pki')
    cert_path = path.join(pki_path, normalized_domain + '.crt')
    key_path = path.join(pki_path, normalized_domain + '.key')
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
    debug(f"get_client_certificates: {domain} {cert_path} {key_path}")
    if await file_exists(cert_path) and await file_exists(key_path):
        return cert_path, key_path
    cert_data_b64 = client_cert_config.cert
    key_data_b64 = client_cert_config.key
    await decode_write_b64(cert_path, cert_data_b64)
    await decode_write_b64(key_path, key_data_b64)
    return cert_path, key_path


async def init_ssl_context() -> SSLContext:
    context = SSLContext(PROTOCOL_TLS)
    verifiy_server_cert = getenv('VERIFY_SERVER_CERT', 'True') == 'True'
    debug(f"verifiy_server_cert: {verifiy_server_cert}")
    if not verifiy_server_cert:
        debug("server certificate verification disabled")
    context.verify_mode = CERT_REQUIRED if verifiy_server_cert else CERT_NONE  # noqa: E501
    context.check_hostname = verifiy_server_cert
    return context


async def get_pki_path() -> str:
    current_path = path.dirname(path.realpath(__file__))
    return path.join(current_path, 'pki')


async def get_ca_server_certificates(
    domain: str,
    config: IdpClientCertConfig
) -> SSLContext:
    debug(f"get_ca_server_certificates: {domain}")
    pki_path = await get_pki_path()
    ca_path = path.join(pki_path, 'ca.pem')
    context = await init_ssl_context()
    client_certificates = await get_client_certificates(domain, config)
    if await file_exists(ca_path):
        debug(f"ca certificate found: {ca_path}")
        context.load_verify_locations(cafile=ca_path)
    context.load_cert_chain(
        certfile=client_certificates[0],
        keyfile=client_certificates[1],
    )
    return context


def is_https(url: str):
    parsed_url = parse.urlparse(url)
    return parsed_url.scheme == 'https' or not parsed_url.scheme == 'http'


async def get_https_certificates(url: str, config: IdpDomainConfig):
    if url and is_https(url):
        return await get_client_certificates(
            config.domain, config.client_cert_config)
    return None


async def get_url_domain(url: str):
    parsed_url = parse.urlparse(url)
    return parsed_url.netloc


async def get_verify_context(url: str, config: IdpDomainConfig) -> Union[SSLContext, Literal[False]]:  # noqa: E501
    debug(f"get_verify_context: {url}")
    if url and is_https(url):
        domain = await get_url_domain(url)
        return await get_ca_server_certificates(domain, config.client_cert_config)  # noqa: E501
    return False
