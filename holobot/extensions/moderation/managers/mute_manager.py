from .imute_manager import IMuteManager
from .. import IConfigProvider
from ..constants import MUTED_ROLE_NAME
from ..exceptions import RoleNotFoundError
from datetime import timedelta
from discord.abc import GuildChannel
from discord.guild import Guild
from discord.errors import Forbidden
from discord.role import Role
from discord.utils import get
from holobot.discord.sdk import IUserManager
from holobot.discord.sdk.exceptions import ForbiddenError
from holobot.sdk.exceptions import ArgumentOutOfRangeError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none
from typing import List, Optional

@injectable(IMuteManager)
class MuteManager(IMuteManager):
    def __init__(self, config_provider: IConfigProvider, user_manager: IUserManager) -> None:
        super().__init__()
        self.__config_provider: IConfigProvider = config_provider
        self.__user_manager: IUserManager = user_manager

    async def mute_user(self, server_id: str, user_id: str, reason: str, duration: Optional[timedelta]) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")
        assert_not_none(reason, "reason")

        reason_length_range = self.__config_provider.get_reason_length_range()
        if not len(reason) in reason_length_range:
            raise ArgumentOutOfRangeError("reason", str(reason_length_range.lower_bound), str(reason_length_range.upper_bound))

        member = self.__user_manager.get_guild_member(server_id, user_id)
        guild = self.__user_manager.get_guild(server_id)
        
        try:
            muted_role = await self.__get_or_create_muted_role(guild, guild.roles)
            await member.add_roles(muted_role)
        except Forbidden:
            raise ForbiddenError()
    
    async def unmute_user(self, server_id: str, user_id: str) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        member = self.__user_manager.get_guild_member(server_id, user_id)
        guild = self.__user_manager.get_guild(server_id)
        muted_role = get(guild.roles, name=MUTED_ROLE_NAME)
        if not muted_role:
            raise RoleNotFoundError(MUTED_ROLE_NAME)
        
        try:
            await member.remove_roles(muted_role)
        except Forbidden:
            raise ForbiddenError()
    
    async def __get_or_create_muted_role(self, guild: Guild, roles: List[Role]) -> Role:
        role = get(roles, name=MUTED_ROLE_NAME)
        if role is not None:
            return role

        role = await guild.create_role(name=MUTED_ROLE_NAME, reason="Used for muting people in text channels.")
        for channel in guild.channels:
            channel: GuildChannel
            await channel.set_permissions(role, send_messages=False)
        return role
