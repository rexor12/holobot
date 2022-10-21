from abc import ABCMeta, abstractmethod
from collections.abc import Mapping

from hikari import Guild, GuildChannel, Member, Role, Snowflake, Snowflakeish, User

class IBot(metaclass=ABCMeta):
    @abstractmethod
    async def get_user_by_id(self, user_id: Snowflakeish) -> User:
        ...

    @abstractmethod
    async def get_guild_by_id(self, guild_id: Snowflakeish) -> Guild:
        ...

    @abstractmethod
    async def get_guild_channel(
        self,
        guild_or_id: Snowflakeish | Guild,
        channel_id: Snowflakeish
    ) -> GuildChannel:
        ...

    @abstractmethod
    async def get_guild_member(
        self,
        guild_or_id: Snowflakeish | Guild,
        user_id: Snowflakeish
    ) -> Member:
        ...

    @abstractmethod
    async def get_guild_member_by_name(
        self,
        guild_or_id: Snowflakeish | Guild,
        user_name: str
    ) -> Member:
        ...

    @abstractmethod
    async def get_guild_role(
        self,
        guild_or_id: Snowflakeish | Guild,
        role_id: Snowflakeish
    ) -> Role:
        ...

    @abstractmethod
    async def get_guild_roles(self, guild_or_id: Snowflakeish | Guild) -> Mapping[Snowflake, Role]:
        ...
