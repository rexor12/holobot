from .imenu_item import IMenuItem
from .models import MenuItemResponse, ServerUserInteractionContext
from typing import Any

class IUserMenuItem(IMenuItem):
    @property
    def name(self) -> str:
        return self.__name
    
    @name.setter
    def name(self, value: str) -> None:
        self.__name = value

    async def execute(self, context: ServerUserInteractionContext, **kwargs: Any) -> MenuItemResponse:
        raise NotImplementedError

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, IUserMenuItem):
            return False
        return self.name < other.name
