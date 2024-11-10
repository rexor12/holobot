from dataclasses import dataclass

from .component_base import ComponentBase

@dataclass(kw_only=True)
class InteractableComponentBase(ComponentBase):
    """Base class for a component that can be interacted with."""

    owner_id: int
    """The identifier of the user who owns the component."""
