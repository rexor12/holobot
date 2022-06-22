from .imenu_item import IMenuItem
from .models import MenuItemResponse, ServerUserInteractionContext
from typing import Any

class IUserMenuItem(IMenuItem):
    async def execute(self, context: ServerUserInteractionContext, **kwargs: Any) -> MenuItemResponse:
        raise NotImplementedError
