from dataclasses import dataclass
from typing import Union

@dataclass
class Choice:
    """Describes a choice of an option of a command."""

    name: str
    """The user-friendly name of the choice."""

    value: Union[str, int, float]
    """The associated value that is provided by Discord
    when the user selects this choice.
    """
