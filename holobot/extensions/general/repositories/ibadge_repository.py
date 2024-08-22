from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.general.models import Badge
from holobot.extensions.general.sdk.badges.models import BadgeId
from holobot.sdk.database.repositories import IRepository

class IBadgeRepository(IRepository[BadgeId, Badge], Protocol):
    def get_badge_name(self, badge_id: BadgeId) -> Awaitable[str | None]:
        ...
