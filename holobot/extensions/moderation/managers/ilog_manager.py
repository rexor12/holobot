from typing import Optional

class ILogManager:
    async def set_log_channel(self, server_id: str, channel_id: Optional[str]) -> None:
        raise NotImplementedError
    
    async def publish_log_entry(self, server_id: str, message: str) -> bool:
        raise NotImplementedError
