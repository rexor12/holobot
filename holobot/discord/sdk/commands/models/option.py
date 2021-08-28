from .choice import Choice
from ..enums import OptionType
from dataclasses import dataclass, field
from typing import List

@dataclass
class Option:
    """Describes an option of a command."""

    name: str
    description: str
    type: OptionType = OptionType.STRING
    is_mandatory: bool = True
    choices: List[Choice] = field(default_factory=lambda: [])
