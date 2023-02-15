from datetime import timedelta
from typing import Protocol

from holobot.extensions.moderation.models import WarnStrike
from holobot.sdk.database.repositories import IRepository
from holobot.sdk.queries import PaginationResult

class IWarnRepository(IRepository[int, WarnStrike], Protocol):
    async def get_warn_count_by_user(self, server_id: str, user_id: str) -> int:
        ...

    async def get_warns_by_user(
        self,
        server_id: str,
        user_id: str,
        page_index: int,
        max_count: int
    ) -> PaginationResult[WarnStrike]:
        ...

    async def add_warn(
        self,
        warn_strike: WarnStrike,
        decay_threshold: timedelta | None = None
    ) -> int:
        ...

    async def clear_warns_by_server(self, server_id: str) -> int:
        ...

    async def clear_warns_by_user(self, server_id: str, user_id: str) -> int:
        ...

    async def clear_expired_warns(self) -> int:
        ...
