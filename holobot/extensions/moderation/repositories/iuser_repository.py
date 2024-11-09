from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.moderation.models import User
from holobot.sdk.database.repositories import IRepository
from holobot.sdk.queries import PaginationResult

class IUserRepository(IRepository[int, User], Protocol):
    def get_by_server(
        self,
        server_id: int,
        user_id: int
    ) -> Awaitable[User | None]:
        ...

    def delete_by_server(
        self,
        server_id: int,
        user_id: int
    ) -> Awaitable[int]:
        ...

    def get_moderators(
        self,
        server_id: int,
        page_index: int,
        page_size: int
    ) -> Awaitable[PaginationResult[User]]:
        ...
