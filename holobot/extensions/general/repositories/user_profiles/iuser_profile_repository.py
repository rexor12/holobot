from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.general.models.user_profiles import RankingInfo, UserProfile
from holobot.extensions.general.sdk.badges.models.badge_id import BadgeId
from holobot.sdk.database.repositories import IRepository
from holobot.sdk.queries import PaginationResult

class IUserProfileRepository(IRepository[int, UserProfile], Protocol):
    def paginate_rankings(
        self,
        page_index: int,
        page_size: int
    ) -> Awaitable[PaginationResult[RankingInfo]]:
        ...

    def is_badge_equipped(
        self,
        user_id: int,
        badge_id: BadgeId
    ) -> Awaitable[bool]:
        ...
