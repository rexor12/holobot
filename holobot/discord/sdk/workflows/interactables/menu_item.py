from dataclasses import dataclass

from .interactable import Interactable
from .enums import MenuType

@dataclass(kw_only=True)
class MenuItem(Interactable):
    name: str
    """The globally unique name of the menu item."""

    title: str
    """The user-friendly title of the context menu item."""

    menu_type: MenuType
    """The type of the containing context menu."""

    # TODO Instead of hard-coding this, move it to configuration.
    index: int
    """The index of the menu item in the context menu."""
    
    def describe(self) -> str:
        return f"MenuItem(name={self.name})"
