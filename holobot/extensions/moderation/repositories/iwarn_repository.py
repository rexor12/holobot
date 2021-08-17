from ..models import WarnStrike
from datetime import timedelta
from typing import Optional, Tuple

class IWarnRepository:
    async def get_warn_count_by_user(self, server_id: str, user_id: str) -> int:
        raise NotImplementedError

    async def get_warns_by_user(self, server_id: str, user_id: str, start_offset: int, max_count: int) -> Tuple[WarnStrike, ...]:
        raise NotImplementedError

    async def add_warn(self, warn_strike: WarnStrike, decay_threshold: Optional[timedelta] = None) -> int:
        raise NotImplementedError
    
    async def clear_warns_by_server(self, server_id: str) -> int:
        raise NotImplementedError
    
    async def clear_warns_by_user(self, server_id: str, user_id: str) -> int:
        raise NotImplementedError
    
    async def clear_expired_warns(self) -> int:
        raise NotImplementedError
