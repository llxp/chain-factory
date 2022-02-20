from aiofiles.os import path as os_path
from aiofiles import open as async_open


async def file_exists(path: str) -> bool:
    return await os_path.exists(path)


async def write_file(path: str, content: bytes):
    async with async_open(path, 'wb') as f:
        await f.write(content)
