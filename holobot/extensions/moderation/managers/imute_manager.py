from datetime import timedelta
from typing import Optional

class IMuteManager:
    async def mute_user(self, server_id: str, user_id: str, reason: str, duration: Optional[timedelta]) -> None:
        raise NotImplementedError
    
    async def unmute_user(self, server_id: str, user_id: str, clear_auto_unmute: bool = True) -> None:
        raise NotImplementedError
