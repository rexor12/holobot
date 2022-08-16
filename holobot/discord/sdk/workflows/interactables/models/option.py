from dataclasses import dataclass, field

from .choice import Choice
from ..enums import OptionType

@dataclass
class Option:
    """Describes an option of a command."""

    name: str
    """The user-friendly name of the option."""

    description: str
    """The user-friendly description of the option."""

    type: OptionType = OptionType.STRING
    """The type of the option."""

    is_mandatory: bool = True
    """Determines whether this option must always be specified."""

    choices: tuple[Choice, ...] = field(default_factory=tuple)
    """An optional list of pre-defined choices that can be selected."""
