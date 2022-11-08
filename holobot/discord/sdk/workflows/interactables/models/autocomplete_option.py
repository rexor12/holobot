from dataclasses import dataclass
from typing import Any

@dataclass(kw_only=True, frozen=True)
class AutocompleteOption:
    """Describes an option of a command partially filled by the user."""

    name: str
    """The user-friendly name of the option."""

    is_focused: bool = False
    """Determines whether this is the option that is currently requesting autocompletion."""

    value: str | Any | None = None
    """The current value of the option.

    An attempt is made to parse the value as the option's specified type,
    however, this may not always be possible in which case it is kept as a string.
    Such a scenario may be a partially filled decimal value.
    """
