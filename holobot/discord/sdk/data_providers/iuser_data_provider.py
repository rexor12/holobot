from collections.abc import AsyncIterable, Awaitable, Iterable
from typing import Protocol

from holobot.discord.sdk.models import UserData

class IUserDataProvider(Protocol):
    def get_user_data_by_id(
        self,
        user_id: int,
        use_cache: bool = True
    ) -> Awaitable[UserData]:
        ...

    def get_user_data_by_ids(
        self,
        user_ids: Iterable[int]
    ) -> AsyncIterable[UserData]:
        ...

    async def get_user_data_by_name(
        self,
        server_id: int,
        user_name: str,
        use_cache: bool = True
    ) -> UserData:
        ...

    def get_self(self) -> UserData:
        ...
