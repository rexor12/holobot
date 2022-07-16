from dataclasses import dataclass, field
from typing import Optional, Tuple

from .interactable import Interactable
from .models import Option

@dataclass(kw_only=True)
class Command(Interactable):
    """Defines a slash command interaction."""

    name: str
    """The name of the command."""

    description: str
    """The user-friendly description of the command."""

    group_name: Optional[str] = None
    """The name of the group the command belongs to, if any."""

    subgroup_name: Optional[str] = None
    """The name of the subgroup within the group, if any.

    Specifying this without specifying a group name will result in an error.
    """

    options: Tuple[Option, ...] = field(default_factory=tuple)
    """The list of arguments the command takes."""
    
    def describe(self) -> str:
        return f"Command(group={self.group_name}, subgroup={self.subgroup_name}, name={self.name})"
