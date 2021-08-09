from enum import IntFlag, unique

@unique
class ModeratorPermission(IntFlag):
    NONE = 0,
    MUTE = 1 << 0,
    KICK = 1 << 1,
    BAN = 1 << 2,
    VIEW_LOGS = 1 << 3
