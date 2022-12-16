from .redis_client import RedisClient
from ..models.list_item_container import ListItem, ListItemContainer
from ..decorators.parse_catcher import parse_catcher


class ListHandler:
    """
    Wrapper class to manage a list in redis in form of a json document
    """

    def __init__(self, list_name: str, redis_client: RedisClient):
        self.list_name = list_name
        self.redis_client = redis_client

    @parse_catcher((AttributeError, TypeError, Exception))
    async def parse_json(self, body: bytes) -> ListItemContainer:
        """
        Decode the redis data to a utf-8 string,
        parse the string to json and
        check, if the data structure fo the parsed object is valid
        """
        decoded = body.decode("utf-8")
        # the from_json method comes from the dataclass_json decorator
        return ListItemContainer.parse_raw(decoded)

    async def clear(self):
        """
        Clear the redis list
        """
        if self.redis_client is not None:
            list_item_container = ListItemContainer()
            # the from_json method comes from the dataclass_json decorator
            return await self.redis_client.set(self.list_name, list_item_container.json())  # noqa: E501
        return False

    async def init(self):
        """
        Initialise the redis list with an empty list
        if the list doesn't exist yet
        """
        if self.redis_client is not None:
            current_list = await self.get()
            if current_list is None:
                list_item_container = ListItemContainer()
                await self.redis_client.set(self.list_name, list_item_container.json())  # noqa: E501

    async def add(self, list_item: ListItem) -> bool:
        """
        Add an entry to the redis list
        """
        if self.redis_client is not None:
            current_list = await self.get()
            if (
                current_list is not None
                and current_list.list_items is not None
                and list_item not in current_list.list_items
            ):
                current_list.list_items.append(list_item)
            else:
                return False
            return await self.redis_client.set(self.list_name, current_list.json())  # noqa: E501
        return False

    async def remove(self, list_item: ListItem) -> bool:
        """
        Remove an entry from the list
        """
        if self.redis_client is not None:
            current_list: ListItemContainer = await self.get()
            if (
                current_list and
                current_list.list_items and
                list_item in current_list.list_items
            ):
                current_list.list_items.remove(list_item)
            else:
                return False
            return await self.redis_client.set(
                self.list_name, current_list.json())
        return False

    async def get(self) -> ListItemContainer:
        """
        get the list
        """
        if self.redis_client:
            content = await self.redis_client.get(self.list_name)
            if content is not None:
                return await self.parse_json(content)
        return None
