from dataclasses import dataclass

from .layout import Layout

@dataclass(kw_only=True)
class InteractableLayoutBase(Layout):
    """Base class for a layout that can be interacted with."""

    owner_id: str
    """The identifier of the user who owns the layout."""
