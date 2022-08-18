from typing import Protocol

from .models import ServerData

class IServerDataProvider(Protocol):
    def get_basic_data_by_id(self, server_id: str) -> ServerData:
        ...
