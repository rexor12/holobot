from .models import MenuItemResponse
from ..enums import Permission
from ..models import InteractionContext
from typing import Any

class IMenuItem:
    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        self.__name = value

    @property
    def required_permissions(self) -> Permission:
        return self.__required_permissions
    
    @required_permissions.setter
    def required_permissions(self, value: Permission) -> None:
        self.__required_permissions = value

    async def execute(self, context: InteractionContext, **kwargs: Any) -> MenuItemResponse:
        """Executes the behavior associated to this context menu item.
        
        Parameters
        ----------
        context : ``InteractionContext``
            The interaction context associated to the request.
            The actual type may be a sub-class of this type.
        
        Returns
        -------
        ``MenuItemResponse``
            The response from the execution of the request.
            The actual type may be a sub-class of this type.
        """

        raise NotImplementedError

    def __lt__(self, other: Any) -> bool:
        return self.name < other.name if isinstance(other, IMenuItem) else False
