from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.general.models import ChannelTimer
from holobot.sdk.database.repositories import IRepository
from holobot.sdk.queries import PaginationResult

class IChannelTimerRepository(IRepository[int, ChannelTimer], Protocol):
    def count_by_server(self, server_id: str) -> Awaitable[int]:
        ...

    def paginate(self, page_index: int, page_size: int) -> Awaitable[PaginationResult[ChannelTimer]]:
        ...

    def remove_all_by_server(self, server_id: str) -> Awaitable[int]:
        ...
