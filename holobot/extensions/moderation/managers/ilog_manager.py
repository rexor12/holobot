from ..models import ModerationLog
from typing import Tuple

class ILogManager:
    # TODO Filter by date.
    async def get_logs(self, server_id: str, start_offset: int, page_size: int) -> Tuple[ModerationLog, ...]:
        raise NotImplementedError
    
    async def clear_logs(self, server_id: str) -> None:
        raise NotImplementedError

    async def set_autolog_channel(self, server_id: str, channel_id: str) -> None:
        raise NotImplementedError
    
    async def disable_autolog(self, server_id: str) -> None:
        raise NotImplementedError
