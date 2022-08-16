from ..models import WarnSettings
from datetime import timedelta

class IWarnSettingsRepository:
    async def get_warn_decay_threshold(self, server_id: str) -> timedelta | None:
        raise NotImplementedError

    async def set_warn_decay_threshold(self, server_id: str, threshold: timedelta) -> None:
        raise NotImplementedError

    async def clear_warn_decay_threshold(self, server_id: str) -> None:
        raise NotImplementedError

    async def get_warn_settings(self, server_id: str) -> WarnSettings:
        raise NotImplementedError

    async def set_auto_mute(self, server_id: str, warn_count: int, duration: timedelta | None) -> None:
        raise NotImplementedError

    async def set_auto_kick(self, server_id: str, warn_count: int) -> None:
        raise NotImplementedError

    async def set_auto_ban(self, server_id: str, warn_count: int) -> None:
        raise NotImplementedError
