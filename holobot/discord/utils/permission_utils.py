from hikari import Permissions

from holobot.discord.sdk.enums import Permission

PERMISSION_TO_DTOS: dict[Permission, Permissions] = {
    Permission.NONE: Permissions.NONE,
    Permission.ADMINISTRATOR: Permissions.ADMINISTRATOR,
    Permission.VIEW_CHANNEL: Permissions.VIEW_CHANNEL,
    Permission.MANAGE_CHANNELS: Permissions.MANAGE_CHANNELS,
    Permission.MANAGE_ROLES: Permissions.MANAGE_ROLES,
    Permission.MANAGE_EMOJIS_AND_STICKERS: Permissions.MANAGE_EMOJIS_AND_STICKERS,
    Permission.VIEW_AUDIT_LOG: Permissions.VIEW_AUDIT_LOG,
    Permission.MANAGE_WEBHOOKS: Permissions.MANAGE_WEBHOOKS,
    Permission.MANAGE_SERVER: Permissions.MANAGE_GUILD,
    Permission.CREATE_INSTANT_INVITE: Permissions.CREATE_INSTANT_INVITE,
    Permission.KICK_MEMBERS: Permissions.KICK_MEMBERS,
    Permission.BAN_MEMBERS: Permissions.BAN_MEMBERS,
    Permission.ADD_REACTIONS: Permissions.ADD_REACTIONS,
    Permission.PRIORITY_SPEAKER: Permissions.PRIORITY_SPEAKER,
    Permission.STREAM: Permissions.STREAM,
    Permission.SEND_MESSAGES: Permissions.SEND_MESSAGES,
    Permission.SEND_TTS_MESSAGES: Permissions.SEND_TTS_MESSAGES,
    Permission.MANAGE_MESSAGES: Permissions.MANAGE_MESSAGES,
    Permission.EMBED_LINKS: Permissions.EMBED_LINKS,
    Permission.ATTACH_FILES: Permissions.ATTACH_FILES,
    Permission.READ_MESSAGE_HISTORY: Permissions.READ_MESSAGE_HISTORY,
    Permission.MENTION_EVERYONE: Permissions.MENTION_ROLES,
    Permission.USE_EXTERNAL_EMOJIS: Permissions.USE_EXTERNAL_EMOJIS,
    Permission.VIEW_SERVER_INSIGHTS: Permissions.VIEW_GUILD_INSIGHTS,
    Permission.JOIN_VOICE_CHANNEL: Permissions.CONNECT,
    Permission.SPEAK_IN_VOICE_CHANNEL: Permissions.SPEAK,
    Permission.MUTE_MEMBERS: Permissions.MUTE_MEMBERS,
    Permission.DEAFEN_MEMBERS: Permissions.DEAFEN_MEMBERS,
    Permission.MOVE_MEMBERS: Permissions.MOVE_MEMBERS,
    Permission.USE_VOICE_ACTIVATION: Permissions.USE_VOICE_ACTIVITY,
    Permission.CHANGE_OWN_NICKNAME: Permissions.CHANGE_NICKNAME,
    Permission.MANAGE_NICKNAMES: Permissions.MANAGE_NICKNAMES,
    Permission.USE_SLASH_COMMANDS: Permissions.USE_APPLICATION_COMMANDS,
    Permission.REQUEST_TO_SPEAK: Permissions.REQUEST_TO_SPEAK
}

PERMISSION_TO_MODELS: dict[Permissions, Permission] = {
    dto: model
    for model, dto in PERMISSION_TO_DTOS.items()
}
