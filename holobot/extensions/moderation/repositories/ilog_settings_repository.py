from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.moderation.models import LogSettings
from holobot.sdk.database.repositories import IRepository

class ILogSettingsRepository(IRepository[int, LogSettings], Protocol):
    def get_by_server(self, server_id: int) -> Awaitable[LogSettings | None]:
        ...

    def delete_by_server(self, server_id: int) -> Awaitable[int]:
        ...
