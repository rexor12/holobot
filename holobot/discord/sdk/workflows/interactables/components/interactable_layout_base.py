from dataclasses import dataclass

from .layout_base import LayoutBase

@dataclass(kw_only=True)
class InteractableLayoutBase(LayoutBase):
    """Base class for a layout that can be interacted with."""

    owner_id: int
    """The identifier of the user who owns the layout."""
