from ..models import Mute
from datetime import datetime
from typing import Optional, Tuple

class IMutesRepository:
    async def get_mute(self, server_id: str, user_id: str) -> Optional[datetime]:
        raise NotImplementedError
    
    async def upsert_mute(self, server_id: str, user_id: str, expires_at: datetime) -> None:
        raise NotImplementedError
    
    async def delete_mute(self, server_id: str, user_id: str) -> int:
        raise NotImplementedError
    
    async def delete_expired_mutes(self) -> Tuple[Mute, ...]:
        raise NotImplementedError
