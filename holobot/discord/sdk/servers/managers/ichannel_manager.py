from collections.abc import Awaitable, Iterable
from datetime import timedelta
from typing import Protocol

from holobot.discord.sdk.servers.models import ServerChannel

class IChannelManager(Protocol):
    def get_channels(
        self,
        server_id: int
    ) -> Awaitable[Iterable[ServerChannel]]:
        ...

    def get_channel_by_id(self, server_id: int, channel_id: int) -> Awaitable[ServerChannel]:
        ...

    def follow_news_channel(
        self,
        server_id: int,
        channel_id: int,
        source_server_id: int,
        source_channel_id: int
    ) -> Awaitable[None]:
        ...

    def unfollow_news_channel_for_all_channels(
        self,
        server_id: int,
        source_server_id: int,
        source_channel_id: int
    ) -> Awaitable[None]:
        ...

    def change_channel_name(self, server_id: int, channel_id: int, name: str) -> Awaitable[None]:
        ...

    def create_thread(
        self,
        server_id: int,
        channel_id: int,
        thread_name: str,
        is_private: bool,
        initial_message: str,
        auto_archive_after: timedelta | None = None,
        can_invite_others: bool = True
    ) -> Awaitable[int]:
        ...

    def add_thread_member(
        self,
        thread_id: int,
        user_id: int
    ) -> Awaitable[None]:
        ...
