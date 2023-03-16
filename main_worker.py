from asyncio import new_event_loop, sleep, set_event_loop
from os import getenv
from worker.main import app
from worker.workflows.vault import Vault

is_dev_mode = getenv('DEV_MODE', 'true').lower() == 'true'


if __name__ == '__main__':
    vault_endpoint: str = getenv('VAULT_URL', 'http://localhost:8004')
    vault_token: str = getenv('VAULT_TOKEN', 's.eBh3bGmUUhADRlJZ3WdbGR7A')
    loop = new_event_loop()
    set_event_loop(loop)
    if not is_dev_mode:
        loop.run_until_complete(Vault.init(
            endpoint=vault_endpoint,
            token=vault_token
        ))
    loop.create_task(app.listen(loop))

    async def run_loop():
        while True:
            try:
                await sleep(1)
            except KeyboardInterrupt:
                break

    loop.run_until_complete(run_loop())
