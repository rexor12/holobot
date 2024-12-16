from dataclasses import dataclass

@dataclass
class ItemBase:
    """Base class for user owned items."""

    count: int
    """The size of the stack of individual but equivalent items."""
