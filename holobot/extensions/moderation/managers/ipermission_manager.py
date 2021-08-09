from ..enums import ModeratorPermission

class IPermissionManager:
    async def add_permissions(self, user_id: str, permissions: ModeratorPermission) -> None:
        raise NotImplementedError
    
    async def remove_permissions(self, user_id: str, permissions: ModeratorPermission) -> None:
        raise NotImplementedError
