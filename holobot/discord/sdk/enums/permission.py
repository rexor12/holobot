from discord import Permissions
from discord.flags import flag_value
from discord.member import Member
from discord.user import User
from enum import IntFlag, unique
from typing import Dict, Union

@unique
class Permission(IntFlag):
    NONE = 0,
    ADMINISTRATOR = 1

discord_map: Dict[Permission, int] = {
    Permission.NONE: Permissions.none().value,
    Permission.ADMINISTRATOR: Permissions.administrator.flag
}

def has_permission(user: Union[User, Member], permissions: Permission) -> bool:
    raise NotImplementedError
