from datetime import datetime
from typing import Protocol

from holobot.extensions.moderation.models import Mute
from holobot.sdk.database.repositories import IRepository

class IMutesRepository(IRepository[int, Mute], Protocol):
    async def upsert_mute(self, server_id: str, user_id: str, expires_at: datetime) -> None:
        ...

    async def delete_mute(self, server_id: str, user_id: str) -> int:
        ...

    async def delete_expired_mutes(self) -> tuple[Mute, ...]:
        ...
