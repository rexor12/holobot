class ILogSettingsRepository:
    async def get_log_channel(self, server_id: str) -> str | None:
        raise NotImplementedError

    async def set_log_channel(self, server_id: str, channel_id: str) -> None:
        raise NotImplementedError

    async def clear_log_channel(self, server_id: str) -> None:
        raise NotImplementedError
