from dataclasses import dataclass
from typing import Literal

from .component_base import ComponentBase

@dataclass(kw_only=True)
class Separator(ComponentBase):
    """
    A component usable in containr components only, that displays a separator line,
    or optionally leaves some blank space between two components.
    """

    has_divider: bool = True
    """Whether the separator line is displayed."""

    spacing: Literal[1] | Literal[2] = 1
    """The size of the spacing."""
