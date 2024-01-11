from collections.abc import Awaitable, Iterable
from typing import Protocol

from holobot.discord.sdk.servers.models import ServerChannel

class IChannelManager(Protocol):
    async def get_channels(
        self,
        server_id: str
    ) -> Iterable[ServerChannel]:
        ...

    def get_channel_by_id(self, server_id: str, channel_id: str) -> Awaitable[ServerChannel]:
        ...

    async def follow_news_channel(
        self,
        server_id: str,
        channel_id: str,
        target_server_id: str,
        target_channel_id: str
    ) -> None:
        ...

    async def unfollow_news_channel_for_all_channels(
        self,
        server_id: str,
        source_server_id: str,
        source_channel_id: str
    ) -> None:
        ...

    def change_channel_name(self, server_id: str, channel_id: str, name: str) -> Awaitable[None]:
        ...
