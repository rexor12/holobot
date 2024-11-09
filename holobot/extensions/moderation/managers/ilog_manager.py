class ILogManager:
    async def set_log_channel(self, server_id: int, channel_id: int | None) -> None:
        raise NotImplementedError

    async def publish_log_entry(self, server_id: int, message: str) -> bool:
        raise NotImplementedError
