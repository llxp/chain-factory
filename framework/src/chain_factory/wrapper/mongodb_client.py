from logging import error
from odmantic import AIOEngine
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure


class MongoDBClient():
    def __init__(
        self,
        uri: str
    ):
        client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
        self.client = AIOEngine(
            client, database=client.get_default_database().name)

    async def check_connection(self):
        try:
            # The ismaster command is cheap and does not require auth.
            # check, if the connection is alive
            await self.client.client.admin.command("ismaster")
        except ConnectionFailure:
            error("Mongodb Server not available")
            raise

    async def close(self):
        pass
