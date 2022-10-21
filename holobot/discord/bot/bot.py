from collections.abc import Mapping

import hikari
from hikari import (
    GatewayBot, Guild, GuildChannel, Intents, Member, Role, Snowflake, Snowflakeish, User
)

from holobot.discord.sdk.exceptions import (
    ChannelNotFoundError, ForbiddenError, RoleNotFoundError, ServerNotFoundError, UserNotFoundError
)
from holobot.sdk.utils.iterable_utils import first_or_default
from holobot.sdk.utils.string_utils import rank_match
from .ibot import IBot

class Bot(GatewayBot, IBot):
    def __init__(self, token: str, intents: Intents):
        super().__init__(token, intents=intents)

    async def get_user_by_id(self, user_id: Snowflakeish) -> User:
        if user := self.cache.get_user(user_id):
            return user

        try:
            return await self.rest.fetch_user(user_id)
        except hikari.NotFoundError as error:
            raise UserNotFoundError(str(user_id)) from error
        except hikari.ForbiddenError as error:
            raise ForbiddenError(f"Failed to fetch user with identifier '{user_id}'.") from error

    async def get_guild_by_id(self, guild_id: Snowflakeish) -> Guild:
        if guild := self.cache.get_available_guild(guild_id):
            return guild

        try:
            return await self.rest.fetch_guild(guild_id)
        except hikari.NotFoundError as error:
            raise ServerNotFoundError(str(guild_id)) from error
        except hikari.ForbiddenError as error:
            raise ForbiddenError(
                f"Failed to fetch server with identifier '{guild_id}'."
            ) from error

    async def get_guild_channel(
        self,
        guild_or_id: Snowflakeish | Guild,
        channel_id: Snowflakeish
    ) -> GuildChannel:
        guild = (
            guild_or_id
            if isinstance(guild_or_id, Guild)
            else await self.get_guild_by_id(guild_or_id)
        )
        if channel := guild.get_channel(channel_id):
            return channel

        try:
            channels = await self.rest.fetch_guild_channels(guild)
            if channel := first_or_default(channels, lambda i: i.id == channel_id):
                return channel

            raise ChannelNotFoundError(str(channel_id), str(guild_or_id))
        except hikari.NotFoundError as error:
            raise ChannelNotFoundError(str(channel_id), str(guild_or_id)) from error
        except hikari.ForbiddenError as error:
            raise ForbiddenError(
                f"Failed to fetch channel with identifier '{channel_id}'"
                f" for server with identifier '{guild_or_id}'."
            ) from error

    async def get_guild_member(
        self,
        guild_or_id: Snowflakeish | Guild,
        user_id: Snowflakeish
    ) -> Member:
        guild = (
            guild_or_id
            if isinstance(guild_or_id, Guild)
            else await self.get_guild_by_id(guild_or_id)
        )
        if member := guild.get_member(int(user_id)):
            return member

        try:
            return await self.rest.fetch_member(guild, user_id)
        except hikari.NotFoundError as error:
            raise UserNotFoundError(str(user_id)) from error
        except hikari.ForbiddenError as error:
            raise ForbiddenError(
                f"Failed to fetch member with identifier '{user_id}'"
                f" for server with identifier '{guild.id}'."
            ) from error

    async def get_guild_member_by_name(
        self,
        guild_or_id: Snowflakeish | Guild,
        user_name: str
    ) -> Member:
        guild = (
            guild_or_id
            if isinstance(guild_or_id, Guild)
            else await self.get_guild_by_id(guild_or_id)
        )
        relevant_members = list[tuple[Member, int]]()
        for member in guild.get_members().values():
            relevance = Bot.__match_user_with_relevance(user_name, member)
            if relevance > 0:
                relevant_members.append((member, relevance))

        best_match = first_or_default(sorted(relevant_members, key=lambda p: p[1], reverse=True))
        if not best_match:
            raise UserNotFoundError(user_name)

        return best_match[0]

    async def get_guild_role(
        self,
        guild_or_id: Snowflakeish | Guild,
        role_id: Snowflakeish
    ) -> Role:
        guild = (
            guild_or_id
            if isinstance(guild_or_id, Guild)
            else await self.get_guild_by_id(guild_or_id)
        )
        if role := guild.get_role(role_id):
            return role

        try:
            roles = await self.rest.fetch_roles(guild)
            if role := first_or_default(roles, lambda i: i.id == role_id):
                return role

            raise RoleNotFoundError(str(guild_or_id), str(role_id))
        except hikari.NotFoundError as error:
            raise RoleNotFoundError(str(role_id), str(guild_or_id)) from error
        except hikari.ForbiddenError as error:
            raise ForbiddenError(
                f"Failed to fetch role with identifier '{role_id}'"
                f" for server with identifier '{guild_or_id}'."
            ) from error

    async def get_guild_roles(self, guild_or_id: Snowflakeish | Guild) -> Mapping[Snowflake, Role]:
        guild = (
            guild_or_id
            if isinstance(guild_or_id, Guild)
            else await self.get_guild_by_id(guild_or_id)
        )
        return guild.get_roles()

    @staticmethod
    def __match_user_with_relevance(pattern: str, user: Member) -> int:
        # Display names are more relevant than real names.
        relevance = rank_match(pattern, user.display_name)
        if relevance > 0:
            return relevance + 1

        return rank_match(pattern, user.username)
