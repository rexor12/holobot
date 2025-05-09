from dataclasses import dataclass, field

from ..enums import OptionType
from .choice import Choice

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

    is_autocomplete: bool = False
    """Determines whether choices are populated by autocompletion.

    When set to true, specified choices are ignored.
    """

    choices: tuple[Choice, ...] = field(default_factory=tuple)
    """An optional list of pre-defined choices that can be selected."""

    argument_name: str | None = None
    """The name of the argument the option maps to."""
