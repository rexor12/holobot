from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.general.models import Marriage
from holobot.sdk.database.repositories import IRepository

class IMarriageRepository(IRepository[int, Marriage], Protocol):
    def get_by_user(
        self,
        server_id: str,
        user_id: str
    ) -> Awaitable[Marriage | None]:
        ...

    def get_by_users(
        self,
        server_id: str,
        user_id1: str,
        user_id2: str
    ) -> Awaitable[Marriage | None]:
        ...

    def delete_by_user(
        self,
        server_id: str,
        user_id1: str,
        user_id2: str
    ) -> Awaitable[bool]:
        ...
