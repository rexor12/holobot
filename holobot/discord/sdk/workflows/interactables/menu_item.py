from dataclasses import dataclass

from .enums import MenuType
from .interactable import Interactable

@dataclass(kw_only=True)
class MenuItem(Interactable):
    title: str
    """The globally unique user-friendly title of the context menu item.

    This also serves as the identifier of the menu item.
    """

    menu_type: MenuType
    """The type of the containing context menu."""

    priority: int
    """The priority of the menu item in the context menu.

    A higher value means the item will appear earlier
    than those with lower values.
    """

    def __str__(self) -> str:
        return f"MenuItem({self.title})"
