from ..bot import BotAccessor
from ..utils import get_guild_member
from discord import Permissions
from discord.abc import GuildChannel, PrivateChannel
from discord.guild import Guild
from discord.member import Member
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.exceptions import ChannelNotFoundError, ServerNotFoundError, UserNotFoundError
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.discord.sdk.servers.models import MemberData
from holobot.discord.utils import get_guild_channel, get_guild
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none, first_or_default
from typing import Dict, List, Optional, Tuple, Union

permission_map: Dict[Permission, int] = {
    Permission.NONE: Permissions.none().value,
    Permission.ADMINISTRATOR: Permissions.administrator.flag,
    Permission.VIEW_CHANNEL: Permissions.view_channel.flag,
    Permission.MANAGE_CHANNELS: Permissions.manage_channels.flag,
    Permission.MANAGE_ROLES: Permissions.manage_roles.flag,
    Permission.MANAGE_EMOJIS_AND_STICKERS: Permissions.manage_emojis.flag,
    Permission.VIEW_AUDIT_LOG: Permissions.view_audit_log.flag,
    Permission.MANAGE_WEBHOOKS: Permissions.manage_webhooks.flag,
    Permission.MANAGE_SERVER: Permissions.manage_guild.flag,
    Permission.CREATE_INSTANT_INVITE: Permissions.create_instant_invite.flag,
    Permission.KICK_MEMBERS: Permissions.kick_members.flag,
    Permission.BAN_MEMBERS: Permissions.ban_members.flag,
    Permission.ADD_REACTIONS: Permissions.add_reactions.flag,
    Permission.PRIORITY_SPEAKER: Permissions.priority_speaker.flag,
    Permission.STREAM: Permissions.stream.flag,
    Permission.SEND_MESSAGES: Permissions.send_messages.flag,
    Permission.SEND_TTS_MESSAGES: Permissions.send_tts_messages.flag,
    Permission.MANAGE_MESSAGES: Permissions.manage_messages.flag,
    Permission.EMBED_LINKS: Permissions.embed_links.flag,
    Permission.ATTACH_FILES: Permissions.attach_files.flag,
    Permission.READ_MESSAGE_HISTORY: Permissions.read_message_history.flag,
    Permission.MENTION_EVERYONE: Permissions.mention_everyone.flag,
    Permission.USE_EXTERNAL_EMOJIS: Permissions.external_emojis.flag,
    Permission.VIEW_SERVER_INSIGHTS: Permissions.view_guild_insights.flag,
    Permission.JOIN_VOICE_CHANNEL: Permissions.connect.flag,
    Permission.SPEAK_IN_VOICE_CHANNEL: Permissions.speak.flag,
    Permission.MUTE_MEMBERS: Permissions.mute_members.flag,
    Permission.DEAFEN_MEMBERS: Permissions.deafen_members.flag,
    Permission.MOVE_MEMBERS: Permissions.move_members.flag,
    Permission.USE_VOICE_ACTIVATION: Permissions.use_voice_activation.flag,
    Permission.CHANGE_OWN_NICKNAME: Permissions.change_nickname.flag,
    Permission.MANAGE_NICKNAMES: Permissions.manage_nicknames.flag,
    Permission.USE_SLASH_COMMANDS: Permissions.use_slash_commands.flag,
    Permission.REQUEST_TO_SPEAK: Permissions.request_to_speak.flag
}

discord_permission_map: Dict[int, Permission] = { value: key for key, value in permission_map.items() }

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
        relevant_members: List[Tuple[Member, int]] = []
        for member in guild.members:
            # An attempt to fix type hints for the messy discord.py.
            member: Member
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
        return first_or_default(guild.members, lambda member: str(member.id) == user_id) is not None

    def get_member_permissions(self, server_id: str, channel_id: str, user_id: str) -> Permission:
        assert_not_none(server_id, "server_id")
        assert_not_none(channel_id, "channel_id")
        assert_not_none(user_id, "user_id")

        channel = get_guild_channel(server_id, channel_id)
        user = get_guild_member(server_id, user_id)
        permissions = channel.permissions_for(user)
        return MemberDataProvider.__transform_permissions(permissions)

    @staticmethod
    def __transform_permissions(discord_permissions: Permissions) -> Permission:
        if discord_permissions == Permissions.none():
            return Permission.NONE

        permissions = Permission.NONE
        flags = discord_permissions.value
        current_flag = 1
        while flags > 0:
            if (flags & current_flag) != current_flag:
                current_flag <<= 1
                continue

            flags ^= current_flag
            if (current_permission := discord_permission_map.get(current_flag, None)) is None:
                current_flag <<= 1
                continue

            permissions |= current_permission
            current_flag <<= 1

        return permissions

    @staticmethod
    def __member_to_basic_data(user: Member) -> MemberData:
        return MemberData(
            user_id=str(user.id), # type: ignore
            avatar_url=user.avatar_url, # type: ignore
            name=user.name, # type: ignore
            nick_name=user.nick
        )

    @staticmethod
    def __match_with_relevance(pattern: str, value: str) -> int:
        relevance = 0
        pattern_lower = pattern.lower()
        value_lower = value.lower()

        # Containment, different casing.
        if not pattern_lower in value_lower:
            return relevance
        relevance = relevance + 1

        # Full match, different casing.
        if pattern_lower == value_lower:
            relevance = relevance + 1
        
        # Containment, same casing.
        if not pattern in value:
            return relevance
        relevance = relevance + 1

        # Full match, same casing.
        if not pattern == value:
            return relevance
        
        return relevance + 1

    @staticmethod
    def __match_user_with_relevance(pattern: str, user: Member) -> int:
        # Display names are more relevant than real names.
        relevance = MemberDataProvider.__match_with_relevance(pattern, user.display_name)
        if relevance > 0:
            return relevance + 1
        return MemberDataProvider.__match_with_relevance(pattern, user.name) # type: ignore
