from typing import Protocol

from holobot.extensions.moderation.models import LogSettings
from holobot.sdk.database.repositories import IRepository

class ILogSettingsRepository(IRepository[int, LogSettings], Protocol):
    async def get_by_server(self, server_id: str) -> LogSettings | None:
        ...

    async def delete_by_server(self, server_id: str) -> None:
        ...
