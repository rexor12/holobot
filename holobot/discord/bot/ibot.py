from collections.abc import Awaitable, Iterable, Mapping, Sequence
from typing import Protocol

import hikari

class IBot(Protocol):
    async def get_user_by_id(
        self,
        user_id: hikari.Snowflakeish,
        use_cache: bool = True
    ) -> hikari.User:
        ...

    async def get_guild_by_id(
        self,
        guild_id: hikari.Snowflakeish
    ) -> hikari.Guild:
        ...

    async def get_guild_channel(
        self,
        guild_or_id: hikari.Snowflakeish | hikari.Guild,
        channel_id: hikari.Snowflakeish
    ) -> hikari.GuildChannel:
        ...

    async def get_guild_member(
        self,
        guild_or_id: hikari.Snowflakeish | hikari.Guild,
        user_id: hikari.Snowflakeish,
        use_cache: bool = True
    ) -> hikari.Member:
        ...

    def get_guild_members(
        self,
        guild_or_id: hikari.Snowflakeish | hikari.Guild,
        user_ids: Iterable[hikari.Snowflakeish],
        use_cache: bool = True
    ) -> Awaitable[Sequence[hikari.Member]]:
        ...

    async def get_guild_member_by_name(
        self,
        guild_or_id: hikari.Snowflakeish | hikari.Guild,
        user_name: str,
        use_cache: bool = True
    ) -> hikari.Member:
        ...

    async def get_guild_role(
        self,
        guild_or_id: hikari.Snowflakeish | hikari.Guild,
        role_id: hikari.Snowflakeish
    ) -> hikari.Role:
        ...

    async def get_guild_roles(
        self,
        guild_or_id: hikari.Snowflakeish | hikari.Guild
    ) -> Mapping[hikari.Snowflake, hikari.Role]:
        ...
