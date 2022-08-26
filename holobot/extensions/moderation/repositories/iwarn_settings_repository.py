from typing import Protocol

from holobot.extensions.moderation.models import WarnSettings
from holobot.sdk.database.repositories import IRepository

class IWarnSettingsRepository(IRepository[int, WarnSettings], Protocol):
    async def get_by_server(self, server_id: str) -> WarnSettings | None:
        ...
