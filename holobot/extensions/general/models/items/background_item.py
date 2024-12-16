from dataclasses import dataclass

from .item_base import ItemBase

@dataclass
class BackgroundItem(ItemBase):
    """A user profile background type item."""

    background_id: int
    """The identifier of the user profile background."""
