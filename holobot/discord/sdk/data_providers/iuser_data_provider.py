from collections.abc import AsyncIterable, Iterable
from typing import Protocol

from holobot.discord.sdk.models import UserData

class IUserDataProvider(Protocol):
    async def get_user_data_by_id(
        self,
        user_id: str,
        use_cache: bool = True
    ) -> UserData:
        ...

    def get_user_data_by_ids(
        self,
        user_ids: Iterable[str]
    ) -> AsyncIterable[UserData]:
        ...

    async def get_user_data_by_name(
        self,
        server_id: str,
        user_name: str,
        use_cache: bool = True
    ) -> UserData:
        ...

    def get_self(self) -> UserData:
        ...
