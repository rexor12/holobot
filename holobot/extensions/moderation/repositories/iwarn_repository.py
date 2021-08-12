from ..models import WarnStrike
from datetime import timedelta
from typing import Optional, Tuple

class IWarnRepository:
    async def get_warns_by_user(self, server_id: str, user_id: str, start_offset: int, max_count: int) -> Tuple[WarnStrike, ...]:
        raise NotImplementedError

    async def add_warn(self, warn_strike: WarnStrike, decay_threshold: Optional[timedelta] = None) -> int:
        raise NotImplementedError
    
    async def clear_warns_by_server(self, server_id: str) -> None:
        raise NotImplementedError
    
    async def clear_warns_by_user(self, server_id: str, user_id: str) -> None:
        raise NotImplementedError
    
    async def clear_warns_older_than(self, threshold: timedelta) -> None:
        raise NotImplementedError
