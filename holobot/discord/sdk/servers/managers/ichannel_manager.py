from collections.abc import Iterable
from typing import Protocol

from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.servers.models import ServerChannel

class IChannelManager(Protocol):
    def get_channels(
        self,
        server_id: str
    ) -> Iterable[ServerChannel]:
        ...

    async def set_role_permissions(
        self,
        server_id: str,
        channel_id: str,
        role_id: str,
        *permissions: tuple[Permission, bool | None]
    ) -> None:
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
