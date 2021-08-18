from ..models import WarnStrike
from datetime import timedelta
from typing import Optional, Tuple

class IWarnManager:
    async def get_warns(self, server_id: str, user_id: str, page_index: int, page_size: int) -> Tuple[WarnStrike, ...]:
        raise NotImplementedError
    
    async def warn_user(self, server_id: str, user_id: str, reason: str, warner_id: str) -> WarnStrike:
        raise NotImplementedError
    
    async def clear_warns_for_user(self, server_id: str, user_id: str) -> int:
        raise NotImplementedError
    
    async def clear_warns_for_server(self, server_id: str) -> int:
        raise NotImplementedError
    
    async def enable_auto_mute(self, server_id: str, warn_count: int, duration: Optional[timedelta]) -> None:
        raise NotImplementedError
    
    async def disable_auto_mute(self, server_id: str) -> None:
        raise NotImplementedError
    
    async def enable_auto_kick(self, server_id: str, warn_count: int) -> None:
        raise NotImplementedError
    
    async def disable_auto_kick(self, server_id: str) -> None:
        raise NotImplementedError
    
    async def enable_auto_ban(self, server_id: str, warn_count: int) -> None:
        raise NotImplementedError
    
    async def disable_auto_ban(self, server_id: str) -> None:
        raise NotImplementedError
    
    async def set_warn_decay(self, server_id: str, decay_time: Optional[timedelta]) -> None:
        raise NotImplementedError
