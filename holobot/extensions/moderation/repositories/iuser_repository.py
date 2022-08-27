from typing import Protocol

from holobot.extensions.moderation.models import User
from holobot.sdk.database.repositories import IRepository
from holobot.sdk.queries import PaginationResult

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

    async def get_moderators(
        self,
        server_id: str,
        page_index: int,
        page_size: int
    ) -> PaginationResult[User]:
        ...
