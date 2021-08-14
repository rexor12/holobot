from typing import Optional

class ILogManager:
    async def set_log_channel(self, server_id: str, channel_id: Optional[str]) -> None:
        raise NotImplementedError
