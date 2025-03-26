from collections.abc import Awaitable, Sequence
from typing import Protocol

from holobot.extensions.general.models import Badge
from holobot.extensions.general.models.items import BadgeDisplayInfo
from holobot.extensions.general.sdk.badges.models import BadgeId
from holobot.sdk.database.repositories import IRepository
from holobot.sdk.queries import PaginationResult

class IBadgeRepository(IRepository[BadgeId, Badge], Protocol):
    def get_badge_name(self, badge_id: BadgeId) -> Awaitable[str | None]:
        ...

    def get_display_info(
        self,
        badge_id: BadgeId
    ) -> Awaitable[BadgeDisplayInfo]:
        ...

    def get_display_infos(
        self,
        server_id: int,
        badge_ids: Sequence[int]
    ) -> Awaitable[list[BadgeDisplayInfo]]:
        ...

    def paginate_badge_infos(
        self,
        server_id: int,
        name_part: str | None,
        page_index: int,
        page_size: int
    ) -> Awaitable[PaginationResult[BadgeDisplayInfo]]:
        ...
