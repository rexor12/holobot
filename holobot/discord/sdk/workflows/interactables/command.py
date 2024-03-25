from dataclasses import dataclass, field

from holobot.discord.sdk.enums import Permission
from .interactable import Interactable
from .models import Option

@dataclass(kw_only=True)
class Command(Interactable):
    """Defines a slash command interaction."""

    name: str
    """The name of the command."""

    description: str
    """The user-friendly description of the command."""

    group_name: str | None = None
    """The name of the group the command belongs to, if any."""

    subgroup_name: str | None = None
    """The name of the subgroup within the group, if any.

    Specifying this without specifying a group name will result in an error.
    """

    options: tuple[Option, ...] = field(default_factory=tuple)
    """The list of arguments the command takes."""

    default_permissions: Permission = Permission.NONE
    """The default permissions required for a user to be able to use this command."""

    def __str__(self) -> str:
        return f"{type(self).__name__}({self.group_name}, {self.subgroup_name}, {self.name})"
