from enum import IntFlag, unique

@unique
class ModeratorPermission(IntFlag):
    NONE_USERS = 0
    MUTE_USERS = 1 << 0
    KICK_USERS = 1 << 1
    BAN_USERS = 1 << 2
    VIEW_LOGS = 1 << 3
    WARN_USERS = 1 << 4

    def textify(self) -> str:
        if self == ModeratorPermission.NONE_USERS:
            return "none"
        text = []
        if ModeratorPermission.MUTE_USERS in self:
            text.append("mute users")
        if ModeratorPermission.KICK_USERS in self:
            text.append("kick users")
        if ModeratorPermission.BAN_USERS in self:
            text.append("ban users")
        if ModeratorPermission.VIEW_LOGS in self:
            text.append("view logs")
        if ModeratorPermission.WARN_USERS in self:
            text.append("warn users")
        return ", ".join(text)
