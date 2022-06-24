from ..enums import ModeratorPermission
from abc import ABCMeta, abstractmethod

class IPermissionManager(metaclass=ABCMeta):
    @abstractmethod
    async def add_permissions(self, server_id: str, user_id: str, permissions: ModeratorPermission) -> None:
        ...
    
    @abstractmethod
    async def remove_permissions(self, server_id: str, user_id: str, permissions: ModeratorPermission) -> None:
        ...
    
    @abstractmethod
    async def has_permissions(self, server_id: str, user_id: str, permissions: ModeratorPermission) -> bool:
        ...
