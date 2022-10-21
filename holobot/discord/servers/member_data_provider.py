from collections.abc import Mapping

import hikari

from holobot.discord.bot import get_bot
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.exceptions import UserNotFoundError
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.discord.sdk.servers.models import MemberData
from holobot.discord.utils.permission_utils import PERMISSION_TO_MODELS
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none

@injectable(IMemberDataProvider)
class MemberDataProvider(IMemberDataProvider):
    async def get_basic_data_by_id(
        self,
        server_id: str,
        user_id: str
    ) -> MemberData:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        user = await get_bot().get_guild_member(int(server_id), int(user_id))
        return MemberDataProvider.__member_to_basic_data(user)

    async def get_basic_data_by_name(
        self,
        server_id: str,
        name: str
    ) -> MemberData:
        assert_not_none(server_id, "server_id")
        assert_not_none(name, "name")

        member = await get_bot().get_guild_member_by_name(int(server_id), name)
        return MemberDataProvider.__member_to_basic_data(member)

    async def is_member(self, server_id: str, user_id: str) -> bool:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        try:
            await get_bot().get_guild_member(int(server_id), int(user_id))
            return True
        except UserNotFoundError:
            return False

    async def get_member_permissions(self, server_id: str, channel_id: str, user_id: str) -> Permission:
        assert_not_none(server_id, "server_id")
        assert_not_none(channel_id, "channel_id")
        assert_not_none(user_id, "user_id")

        guild = await get_bot().get_guild_by_id(int(server_id))
        member = await get_bot().get_guild_member(guild, int(user_id))
        # Check if the user the owner of the server, in which case all permissions are granted.
        if member.id == guild.owner_id:
            return Permission.all_permissions()

        # Check if any of the user's roles has the administrator permission.
        roles = await get_bot().get_guild_roles(guild)
        base_permissions = MemberDataProvider._get_role_permissions(member, roles)
        if base_permissions & base_permissions.ADMINISTRATOR:
            return Permission.all_permissions()

        channel = await get_bot().get_guild_channel(guild, int(channel_id))
        if not channel:
            return MemberDataProvider.__transform_permissions(base_permissions)

        channel_permissions = MemberDataProvider._get_channel_permissions(member, channel, base_permissions)
        return MemberDataProvider.__transform_permissions(channel_permissions)

    @staticmethod
    def __transform_permissions(dto: hikari.Permissions) -> Permission:
        if dto is hikari.Permissions.NONE:
            return Permission.NONE

        permissions = Permission.NONE
        flags = dto.value
        current_flag = 1
        while flags > 0:
            if (flags & current_flag) != current_flag:
                current_flag <<= 1
                continue

            flags ^= current_flag
            if (current_permission := PERMISSION_TO_MODELS.get(hikari.Permissions(current_flag))) is None:
                current_flag <<= 1
                continue

            permissions |= int(current_permission)
            current_flag <<= 1

        return permissions

    @staticmethod
    def __member_to_basic_data(user: hikari.Member) -> MemberData:
        bot_user = get_bot().get_me()
        return MemberData(
            user_id=str(user.id),
            avatar_url=user.avatar_url and user.avatar_url.url,
            server_specific_avatar_url=user.guild_avatar_url and user.guild_avatar_url.url,
            name=user.username,
            nick_name=user.nickname,
            is_self=bot_user == user,
            is_bot=user.is_bot
        )

    @staticmethod
    def _get_channel_permissions(
        member: hikari.Member,
        channel: hikari.GuildChannel,
        permissions: hikari.Permissions
    ) -> hikari.Permissions:
        # Get the permissions of "everyone" first.
        if everyone_overwrite := channel.permission_overwrites.get(member.guild_id):
            permissions &= ~everyone_overwrite.deny
            permissions |= everyone_overwrite.allow

        # Then apply the permissions of the member's roles.
        for overwrite in filter(None, map(channel.permission_overwrites.get, member.role_ids)):
            permissions &= ~overwrite.deny
            permissions |= overwrite.allow

        # Then apply the permissions of the channel itself.
        if member_overwrite := channel.permission_overwrites.get(member.user.id):
            permissions &= ~member_overwrite.deny
            permissions |= member_overwrite.allow

        return permissions

    @staticmethod
    def _get_role_permissions(
        member: hikari.Member,
        roles: Mapping[hikari.Snowflake, hikari.Role]
    ) -> hikari.Permissions:
        # Get the "everyone" permissions for the guild.
        permissions = roles[member.guild_id].permissions

        # Apply the permissions of each role the user has.
        for role in map(roles.get, member.role_ids):
            if role and role.id != member.guild_id:
                permissions |= role.permissions

        return permissions
