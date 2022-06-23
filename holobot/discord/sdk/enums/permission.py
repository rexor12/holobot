from __future__ import annotations
from enum import IntFlag, unique

import functools
import operator

@unique
class Permission(IntFlag):
    NONE                        =   0
    ADMINISTRATOR               =   1 << 0
    VIEW_CHANNEL                =   1 << 1
    MANAGE_CHANNELS             =   1 << 2
    MANAGE_ROLES                =   1 << 3
    MANAGE_EMOJIS_AND_STICKERS  =   1 << 4
    VIEW_AUDIT_LOG              =   1 << 5
    MANAGE_WEBHOOKS             =   1 << 6
    MANAGE_SERVER               =   1 << 7
    CREATE_INSTANT_INVITE       =   1 << 8
    KICK_MEMBERS                =   1 << 9
    BAN_MEMBERS                 =   1 << 10
    ADD_REACTIONS               =   1 << 11
    PRIORITY_SPEAKER            =   1 << 12
    STREAM                      =   1 << 13
    SEND_MESSAGES               =   1 << 14
    SEND_TTS_MESSAGES           =   1 << 15
    MANAGE_MESSAGES             =   1 << 16
    EMBED_LINKS                 =   1 << 17
    ATTACH_FILES                =   1 << 18
    READ_MESSAGE_HISTORY        =   1 << 19
    MENTION_EVERYONE            =   1 << 20
    USE_EXTERNAL_EMOJIS         =   1 << 21
    VIEW_SERVER_INSIGHTS        =   1 << 22
    JOIN_VOICE_CHANNEL          =   1 << 23
    SPEAK_IN_VOICE_CHANNEL      =   1 << 24
    MUTE_MEMBERS                =   1 << 25
    DEAFEN_MEMBERS              =   1 << 26
    MOVE_MEMBERS                =   1 << 27
    USE_VOICE_ACTIVATION        =   1 << 28
    CHANGE_OWN_NICKNAME         =   1 << 29
    MANAGE_NICKNAMES            =   1 << 30
    USE_SLASH_COMMANDS          =   1 << 31
    REQUEST_TO_SPEAK            =   1 << 32

    @classmethod
    def all_permissions(cls) -> Permission:
        return functools.reduce(operator.ior, Permission)
