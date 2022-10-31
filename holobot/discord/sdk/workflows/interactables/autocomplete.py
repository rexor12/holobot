from dataclasses import dataclass, field

from .interactable import Interactable

@dataclass(kw_only=True)
class Autocomplete(Interactable):
    """Defines an autocomplete interaction."""

    name: str
    """The name of the command."""

    group_name: str | None = None
    """The name of the group the command belongs to, if any."""

    subgroup_name: str | None = None
    """The name of the subgroup within the group, if any.

    Specifying this without specifying a group name will result in an error.
    """

    options: tuple[str, ...] = field(default_factory=tuple)
    """The names of options the autocomplete handles."""

    def __str__(self) -> str:
        return f"{type(self).__name__}({self.group_name}, {self.subgroup_name}, {self.name})"
