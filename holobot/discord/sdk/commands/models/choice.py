from dataclasses import dataclass
from typing import Union

@dataclass
class Choice:
    """Describes a choice of an option of a command."""

    name: str
    value: Union[str, int, float]
