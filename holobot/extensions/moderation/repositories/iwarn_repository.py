from collections.abc import Awaitable
from datetime import timedelta
from typing import Protocol

from holobot.extensions.moderation.models import WarnStrike
from holobot.sdk.database.repositories import IRepository
from holobot.sdk.queries import PaginationResult

class IWarnRepository(IRepository[int, WarnStrike], Protocol):
    def get_warn_count_by_user(self, server_id: int, user_id: int) -> Awaitable[int]:
        ...

    def get_warns_by_user(
        self,
        server_id: int,
        user_id: int,
        page_index: int,
        max_count: int
    ) -> Awaitable[PaginationResult[WarnStrike]]:
        ...

    def add_warn(
        self,
        warn_strike: WarnStrike,
        decay_threshold: timedelta | None = None
    ) -> Awaitable[int]:
        ...

    def clear_warns_by_server(self, server_id: int) -> Awaitable[int]:
        ...

    def clear_warns_by_user(self, server_id: int, user_id: int) -> Awaitable[int]:
        ...

    def clear_expired_warns(self) -> Awaitable[int]:
        ...
