from datetime import timedelta
from typing import Optional

class IWarnSettingsRepository:
    async def get_warn_decay_threshold(self, server_id: str) -> Optional[timedelta]:
        raise NotImplementedError

    async def set_warn_decay_threshold(self, server_id: str, threshold: timedelta) -> None:
        raise NotImplementedError

    async def clear_warn_decay_threshold(self, server_id: str) -> None:
        raise NotImplementedError
