from base64 import b64decode

from .files import write_file


async def decode_write_b64(path: str, b64: str):
    decoded = b64decode(b64)
    await write_file(path, decoded)
