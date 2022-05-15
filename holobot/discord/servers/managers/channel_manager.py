from discord.abc import GuildChannel
from discord.errors import Forbidden
from discord.role import Role
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.exceptions import ChannelNotFoundError, ForbiddenError, PermissionError, RoleNotFoundError
from holobot.discord.sdk.servers.managers import IChannelManager
from holobot.discord.sdk.servers.models import ServerAudioChannel, ServerChannel
from holobot.discord.transformers.server_channel import remote_to_local
from holobot.discord.utils import get_guild
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none, first_or_default
from typing import Dict, Iterable, List, Optional, Tuple, Union

permission_mapping: Dict[Permission, str] = {
    Permission.ADMINISTRATOR: "administrator",
    Permission.VIEW_CHANNEL: "read_messages",
    Permission.MANAGE_CHANNELS: "manage_channels",
    Permission.MANAGE_ROLES: "manage_roles",
    Permission.MANAGE_EMOJIS_AND_STICKERS: "manage_emojis",
    Permission.VIEW_AUDIT_LOG: "view_audit_log",
    Permission.MANAGE_WEBHOOKS: "manage_webhooks",
    Permission.MANAGE_SERVER: "manage_guild",
    Permission.CREATE_INSTANT_INVITE: "create_instant_invite",
    Permission.KICK_MEMBERS: "kick_members",
    Permission.BAN_MEMBERS: "ban_members",
    Permission.ADD_REACTIONS: "add_reactions",
    Permission.PRIORITY_SPEAKER: "priority_speaker",
    Permission.STREAM: "stream",
    Permission.SEND_MESSAGES: "send_messages",
    Permission.SEND_TTS_MESSAGES: "send_tts_messages",
    Permission.MANAGE_MESSAGES: "manage_messages",
    Permission.EMBED_LINKS: "embed_links",
    Permission.ATTACH_FILES: "attach_files",
    Permission.READ_MESSAGE_HISTORY: "read_message_history",
    Permission.MENTION_EVERYONE: "mention_everyone",
    Permission.USE_EXTERNAL_EMOJIS: "external_emojis",
    Permission.VIEW_SERVER_INSIGHTS: "view_guild_insights",
    Permission.JOIN_VOICE_CHANNEL: "connect",
    Permission.SPEAK_IN_VOICE_CHANNEL: "speak",
    Permission.MUTE_MEMBERS: "mute_members",
    Permission.DEAFEN_MEMBERS: "deafen_members",
    Permission.MOVE_MEMBERS: "move_members",
    Permission.USE_VOICE_ACTIVATION: "use_voice_activation",
    Permission.CHANGE_OWN_NICKNAME: "change_nickname",
    Permission.MANAGE_NICKNAMES: "manage_nicknames",
    Permission.USE_SLASH_COMMANDS: "use_slash_commands",
    Permission.REQUEST_TO_SPEAK: "request_to_speak"
}

@injectable(IChannelManager)
class ChannelManager(IChannelManager):
    def get_audio_channel(self, server_id: str, channel_id: str) -> Optional[ServerAudioChannel]:
        assert_not_none(server_id, "server_id")
        assert_not_none(channel_id, "channel_id")

        guild = get_guild(server_id)
        channels: List[GuildChannel] = guild.channels
        channel = first_or_default(channels, lambda c: str(c.id) == channel_id) # type: ignore
        return ServerAudioChannel(
            id=str(channel.id), # type: ignore
            server_id=server_id,
            name=channel.name, # type: ignore
            member_ids=[member.id for member in channel.members] # type: ignore
        )

    def get_channels(self, server_id: str) -> Iterable[ServerChannel]:
        assert_not_none(server_id, "server_id")

        guild = get_guild(server_id)
        channels: List[GuildChannel] = guild.channels
        return [remote_to_local(channel, server_id) for channel in channels]

    async def set_role_permissions(self, server_id: str, channel_id: str, role_id: str, *permissions: Tuple[Permission, Union[bool, None]]) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(channel_id, "channel_id")
        assert_not_none(role_id, "role_id")

        if len(permissions) == 0:
            return

        guild = get_guild(server_id)
        channel: Optional[GuildChannel] = guild.get_channel(int(channel_id))
        if not channel:
            raise ChannelNotFoundError(channel_id)

        role: Optional[Role] = guild.get_role(int(role_id))
        if not role:
            raise RoleNotFoundError(server_id, role_id)

        discord_permissions: Dict[str, Union[bool, None]] = {}
        for permission, status in permissions:
            if (permission_name := permission_mapping.get(permission, None)) is None:
                # This may also be a programming error if the map doesn't contain a newly introduced flag.
                raise PermissionError(permission, "There is no matching Discord permission. Make sure a single flag is specified only.")
            discord_permissions[permission_name] = status

        try:
            await channel.set_permissions(role, **discord_permissions)
        except Forbidden:
            raise ForbiddenError(f"Cannot set permissions for role '{role_id}' and channel '{channel_id}'.")
