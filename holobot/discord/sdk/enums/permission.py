from enum import IntFlag, unique

@unique
class Permission(IntFlag):
    NONE = 0
    ADMINISTRATOR = 1 << 0
    VIEW_CHANNEL = 1 << 1
    MANAGE_CHANNELS = 1 << 2
    MANAGE_ROLES = 1 << 3
    MANAGE_EMOJIS_AND_STICKERS = 1 << 4
    VIEW_AUDIT_LOG = 1 << 5
    MANAGE_WEBHOOKS = 1 << 6
    MANAGE_SERVER = 1 << 7
