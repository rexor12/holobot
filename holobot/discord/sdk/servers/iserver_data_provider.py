from typing import Protocol

from .models import ServerData

class IServerDataProvider(Protocol):
    async def get_basic_data_by_id(self, server_id: int) -> ServerData:
        ...
