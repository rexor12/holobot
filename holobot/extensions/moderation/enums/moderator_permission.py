from enum import IntFlag, unique

@unique
class ModeratorPermission(IntFlag):
    NONE = 0
    MUTE_USERS = 1 << 0
    KICK_USERS = 1 << 1
    BAN_USERS = 1 << 2
    WARN_USERS = 1 << 3

    def textify(self) -> str:
        if self == ModeratorPermission.NONE:
            return "none"
        text = []
        if ModeratorPermission.MUTE_USERS in self:
            text.append("mute users")
        if ModeratorPermission.KICK_USERS in self:
            text.append("kick users")
        if ModeratorPermission.BAN_USERS in self:
            text.append("ban users")
        if ModeratorPermission.WARN_USERS in self:
            text.append("warn users")
        return ", ".join(text)
