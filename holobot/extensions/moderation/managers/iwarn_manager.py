from ..models import WarnStrike
from datetime import timedelta
from typing import Tuple

class IWarnManager:
    async def get_warns(self, server_id: str, user_id: str, start_offset: int, page_size: int) -> Tuple[WarnStrike, ...]:
        raise NotImplementedError
    
    async def clear_warns_for_user(self, server_id: str, user_id: str) -> None:
        raise NotImplementedError
    
    async def clear_warns_for_server(self, server_id: str) -> None:
        raise NotImplementedError
    
    async def enable_auto_mute(self, server_id: str, warn_count: int, duration: timedelta) -> None:
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
    
    async def set_warn_decay(self, server_id: str, decay_time: timedelta) -> None:
        raise NotImplementedError
