from ..utils import get_guild_member
from ..utils.permission_utils import PERMISSION_TO_MODELS
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.exceptions import UserNotFoundError
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.discord.sdk.servers.models import MemberData
from holobot.discord.utils import get_guild_channel, get_guild
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none, first_or_default
from typing import List, Mapping, Tuple

import hikari

@injectable(IMemberDataProvider)
class MemberDataProvider(IMemberDataProvider):
    def get_basic_data_by_id(self, server_id: str, user_id: str) -> MemberData:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        user = get_guild_member(server_id, user_id)
        return MemberDataProvider.__member_to_basic_data(user)

    def get_basic_data_by_name(self, server_id: str, name: str) -> MemberData:
        assert_not_none(server_id, "server_id")
        assert_not_none(name, "name")

        guild = get_guild(server_id)
        relevant_members: List[Tuple[hikari.Member, int]] = []
        for member in guild.get_members().values():
            relevance = MemberDataProvider.__match_user_with_relevance(name, member)
            if relevance > 0:
                relevant_members.append((member, relevance))

        best_match = first_or_default(sorted(relevant_members, key=lambda p: p[1], reverse=True))
        if not best_match:
            raise UserNotFoundError(name)

        return MemberDataProvider.__member_to_basic_data(best_match[0])

    def is_member(self, server_id: str, user_id: str) -> bool:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        guild = get_guild(server_id)
        return first_or_default(guild.get_members().values(), lambda member: str(member.id) == user_id) is not None

    def get_member_permissions(self, server_id: str, channel_id: str, user_id: str) -> Permission:
        assert_not_none(server_id, "server_id")
        assert_not_none(channel_id, "channel_id")
        assert_not_none(user_id, "user_id")

        guild = get_guild(server_id)
        member = get_guild_member(server_id, user_id)
        # Check if the user the owner of the server, in which case all permissions are granted.
        if member.id == guild.owner_id:
            return Permission.all_permissions()

        # Check if any of the user's roles has the administrator permission.
        roles = guild.get_roles()
        base_permissions = MemberDataProvider._get_role_permissions(member, roles)
        if base_permissions & base_permissions.ADMINISTRATOR:
            return Permission.all_permissions()

        channel = get_guild_channel(server_id, channel_id)
        if not channel:
            return MemberDataProvider.__transform_permissions(base_permissions)

        channel_permissions = MemberDataProvider._get_channel_permissions(member, channel, base_permissions)
        return MemberDataProvider.__transform_permissions(channel_permissions)

    @staticmethod
    def __transform_permissions(dto: hikari.Permissions) -> Permission:
        if dto == hikari.Permissions.NONE:
            return Permission.NONE

        permissions = Permission.NONE
        flags = dto.value
        current_flag = 1
        while flags > 0:
            if (flags & current_flag) != current_flag:
                current_flag <<= 1
                continue

            flags ^= current_flag
            if (current_permission := PERMISSION_TO_MODELS.get(hikari.Permissions(current_flag), None)) is None:
                current_flag <<= 1
                continue

            permissions |= int(current_permission)
            current_flag <<= 1

        return permissions

    @staticmethod
    def __member_to_basic_data(user: hikari.Member) -> MemberData:
        return MemberData(
            user_id=str(user.id),
            avatar_url=user.avatar_url.url if user.avatar_url else None,
            name=user.username,
            nick_name=user.nickname
        )

    @staticmethod
    def __match_with_relevance(pattern: str, value: str) -> int:
        relevance = 0
        pattern_lower = pattern.lower()
        value_lower = value.lower()

        # Containment, different casing.
        if pattern_lower not in value_lower:
            return relevance
        relevance += 1

        # Full match, different casing.
        if pattern_lower == value_lower:
            relevance += 1

        # Containment, same casing.
        if pattern not in value:
            return relevance
        relevance += 1

        # Full match, same casing.
        if pattern != value:
            return relevance

        return relevance + 1

    @staticmethod
    def __match_user_with_relevance(pattern: str, user: hikari.Member) -> int:
        # Display names are more relevant than real names.
        relevance = MemberDataProvider.__match_with_relevance(pattern, user.display_name)
        if relevance > 0:
            return relevance + 1
        return MemberDataProvider.__match_with_relevance(pattern, user.username)

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
