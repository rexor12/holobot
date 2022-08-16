from datetime import datetime

from ..models import Mute

class IMutesRepository:
    async def get_mute(self, server_id: str, user_id: str) -> datetime | None:
        raise NotImplementedError

    async def upsert_mute(self, server_id: str, user_id: str, expires_at: datetime) -> None:
        raise NotImplementedError

    async def delete_mute(self, server_id: str, user_id: str) -> int:
        raise NotImplementedError

    async def delete_expired_mutes(self) -> tuple[Mute, ...]:
        raise NotImplementedError
