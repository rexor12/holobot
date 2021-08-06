from ..enums import Permission
from ..exceptions import PermissionError
from discord import Permissions
from typing import Dict, Optional

discord_map: Dict[Permission, int] = {
    Permission.NONE: Permissions.none().value,
    Permission.ADMINISTRATOR: Permissions.administrator.flag,
    Permission.VIEW_CHANNEL: Permissions.view_channel.flag,
    Permission.MANAGE_CHANNELS: Permissions.manage_channels.flag,
    Permission.MANAGE_ROLES: Permissions.manage_roles.flag,
    Permission.MANAGE_EMOJIS_AND_STICKERS: Permissions.manage_emojis.flag,
    Permission.VIEW_AUDIT_LOG: Permissions.view_audit_log.flag,
    Permission.MANAGE_WEBHOOKS: Permissions.manage_webhooks.flag,
    Permission.MANAGE_SERVER: Permissions.manage_guild.flag
}

def has_permissions(user_permissions: Permissions, required_permissions: Permission) -> bool:
    if required_permissions == Permission.NONE:
        return True

    flags = required_permissions.value
    current_flag = 1
    while flags > 0:
        if (flags & current_flag) != current_flag or (current_permission := __parse_flag(current_flag)) is None:
            flags -= flags & current_flag
            current_flag <<= 1
            continue

        if (mapping := discord_map.get(current_permission, None)) is None:
            raise PermissionError(current_permission, "Invalid permission. This is a programming error.")
        
        if (user_permissions.value & mapping) != mapping:
            return False

        flags ^= current_flag
        current_flag <<= 1

    return True

def __parse_flag(flag: int) -> Optional[Permission]:
    try:
        return Permission(flag)
    except ValueError:
        return None
