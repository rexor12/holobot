from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.general.models import UserBadge
from holobot.extensions.general.sdk.badges.models import UserBadgeId
from holobot.sdk.database.repositories import IRepository
from holobot.sdk.queries import PaginationResult

class IUserBadgeRepository(IRepository[UserBadgeId, UserBadge], Protocol):
    def paginate(
        self,
        user_id: str,
        page_index: int,
        page_size: int
    ) -> Awaitable[PaginationResult[UserBadge]]:
        ...

    def exists(self, id: UserBadgeId) -> Awaitable[bool]:
        ...
