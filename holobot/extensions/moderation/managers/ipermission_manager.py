from ..enums import ModeratorPermission

class IPermissionManager:
    async def add_permissions(self, server_id: str, user_id: str, permissions: ModeratorPermission) -> None:
        raise NotImplementedError
    
    async def remove_permissions(self, server_id: str, user_id: str, permissions: ModeratorPermission) -> None:
        raise NotImplementedError
    
    async def has_permissions(self, server_id: str, user_id: str, permissions: ModeratorPermission) -> bool:
        raise NotImplementedError
