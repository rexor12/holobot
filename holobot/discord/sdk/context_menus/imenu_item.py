from .menu_item_response import MenuItemResponse
from ..enums import Permission
from discord_slash.context import MenuContext
from typing import Any

class IMenuItem:
    @property
    def required_permissions(self) -> Permission:
        return self.__required_permissions
    
    @required_permissions.setter
    def required_permissions(self, value: Permission) -> None:
        self.__required_permissions = value

    # Same design as commands.
    async def execute(self, context: MenuContext, **kwargs) -> MenuItemResponse:
        raise NotImplementedError

    def __lt__(self, other: Any) -> bool:
        return False
