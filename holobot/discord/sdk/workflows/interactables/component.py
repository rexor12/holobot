from dataclasses import dataclass, field

from holobot.discord.sdk.workflows.interactables.components import ComponentBase
from .interactable import Interactable

@dataclass(kw_only=True)
class Component(Interactable):
    identifier: str
    """The globally unique identifier of the component.

    The same identifier CANNOT be used by multiple components to avoid ambiguity.
    """

    component_type: type[ComponentBase] = field(repr=False)
    """The type of the component."""
