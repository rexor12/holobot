from dataclasses import dataclass

from .option import Option

@dataclass
class StringOption(Option):
    min_length: int | None = None
    """The minimum length of the input string."""

    max_length: int | None = None
    """The maximum length of the input string."""
