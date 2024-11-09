from datetime import timedelta
from typing import Protocol

from holobot.sdk.queries import PaginationResult
from ..models import WarnStrike

class IWarnManager(Protocol):
    async def get_warns(
        self,
        server_id: int,
        user_id: int,
        page_index: int,
        page_size: int
    ) -> PaginationResult[WarnStrike]:
        ...

    async def warn_user(
        self,
        server_id: int,
        user_id: int,
        reason: str,
        warner_id: int
    ) -> WarnStrike:
        ...

    async def clear_warns_for_user(self, server_id: int, user_id: int) -> int:
        ...

    async def clear_warns_for_server(self, server_id: int) -> int:
        ...

    async def enable_auto_mute(
        self,
        server_id: int,
        warn_count: int,
        duration: timedelta | None
    ) -> None:
        ...

    async def disable_auto_mute(self, server_id: int) -> None:
        ...

    async def enable_auto_kick(self, server_id: int, warn_count: int) -> None:
        ...

    async def disable_auto_kick(self, server_id: int) -> None:
        ...

    async def enable_auto_ban(self, server_id: int, warn_count: int) -> None:
        ...

    async def disable_auto_ban(self, server_id: int) -> None:
        ...

    async def get_warn_decay(self, server_id: int) -> timedelta | None:
        ...

    async def set_warn_decay(
        self,
        server_id: int,
        decay_time: timedelta | None
    ) -> None:
        ...

    async def remove_warn(self, warn_strike_id: int) -> None:
        ...
