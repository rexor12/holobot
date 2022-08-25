from typing import Protocol

from holobot.extensions.moderation.models import User
from holobot.sdk.database.repositories import IRepository

class IUserRepository(IRepository[int, User], Protocol):
    async def get_by_server(
        self,
        server_id: str,
        user_id: str
    ) -> User | None:
        ...

    async def delete_by_server(
        self,
        server_id: str,
        user_id: str
    ) -> None:
        ...
