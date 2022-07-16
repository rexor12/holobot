from dataclasses import dataclass
from typing import Type

from .interactable import Interactable
from holobot.discord.sdk.components import ComponentBase

@dataclass(kw_only=True)
class Component(Interactable):
    identifier: str
    """The globally unique identifier of the component.

    The same identifier CANNOT be used by multiple components to avoid ambiguity.
    """

    component_type: Type[ComponentBase]
    """The type of the component."""
    
    def describe(self) -> str:
        return f"Component(id={self.identifier})"
