from collections.abc import Awaitable
from typing import Protocol

class ILogManager(Protocol):
    def set_log_channel(self, server_id: int, channel_id: int | None) -> Awaitable[None]:
        ...

    def publish_log_entry(self, server_id: int, message: str) -> Awaitable[bool]:
        ...
