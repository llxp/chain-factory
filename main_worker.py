from asyncio import gather, new_event_loop, set_event_loop
from concurrent.futures import ThreadPoolExecutor
from os import getenv
import threading
from worker.main import app
from worker.workflows.vault import Vault

is_dev_mode = getenv('DEV_MODE', 'true').lower() == 'true'


if __name__ == '__main__':
    vault_endpoint: str = getenv('VAULT_URL', 'http://localhost:8004')
    vault_token: str = getenv('VAULT_TOKEN', 's.eBh3bGmUUhADRlJZ3WdbGR7A')
    loop = new_event_loop()
    thread_pool_executor = ThreadPoolExecutor()
    loop.set_default_executor(thread_pool_executor)
    set_event_loop(loop)
    if not is_dev_mode:
        loop.run_until_complete(Vault.init(
            endpoint=vault_endpoint,
            token=vault_token
        ))
    print("Thread: ", threading.get_ident())

    tasks = gather(
        app.listen(loop),
        return_exceptions=True
    )

    try:
        # run the task "app.listen" in the event loop
        loop.run_until_complete(tasks)
    except KeyboardInterrupt:
        print("Caught keyboard interrupt. Canceling tasks...")
        # Cancel the app.listen task
        tasks.cancel()
        # run the loop again to ensure the the node is cleaned up properly
        loop.run_forever()
    finally:
        loop.close()
