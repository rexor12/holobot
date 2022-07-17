from dataclasses import dataclass

from .interactable import Interactable
from .enums import MenuType

@dataclass(kw_only=True)
class MenuItem(Interactable):
    title: str
    """The globally unique user-friendly title of the context menu item.
    
    This also serves as the identifier of the menu item.
    """

    menu_type: MenuType
    """The type of the containing context menu."""

    # TODO Instead of hard-coding this, move it to configuration.
    priority: int
    """The priority of the menu item in the context menu.
    
    A higher value means the item will appear earlier
    than those with lower values.
    """
    
    def describe(self) -> str:
        return f"MenuItem(title={self.title})"
