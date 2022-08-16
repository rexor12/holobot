from collections.abc import Sequence
from typing import Protocol

from holobot.discord.sdk.models import Server

class IBotDataProvider(Protocol):
    def get_user_id(self) -> str:
        ...

    def get_avatar_url(self) -> str:
        ...

    def get_latency(self) -> float:
        ...

    def get_server_count(self) -> int:
        ...

    def get_servers(self, page_index: int, page_size: int) -> tuple[int, Sequence[Server]]:
        ...
