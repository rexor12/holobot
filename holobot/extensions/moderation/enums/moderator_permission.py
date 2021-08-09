from enum import IntFlag, unique

@unique
class ModeratorPermission(IntFlag):
    NONE = 0
    MUTE = 1 << 0
    KICK = 1 << 1
    BAN = 1 << 2
    VIEW_LOGS = 1 << 3

    def textify(self) -> str:
        if self == ModeratorPermission.NONE:
            return "none"
        text = []
        if ModeratorPermission.MUTE in self:
            text.append("mute users")
        if ModeratorPermission.KICK in self:
            text.append("kick users")
        if ModeratorPermission.BAN in self:
            text.append("ban users")
        if ModeratorPermission.VIEW_LOGS in self:
            text.append("view logs")
        return ", ".join(text)
