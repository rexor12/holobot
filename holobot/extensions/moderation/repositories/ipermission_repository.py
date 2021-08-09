from ..enums import ModeratorPermission

class IPermissionRepository:
    async def add_user_permissions(self, server_id: str, user_id: str, permissions: ModeratorPermission) -> None:
        raise NotImplementedError
    
    async def remove_user_permissions(self, server_id: str, user_id: str, permissions: ModeratorPermission) -> None:
        raise NotImplementedError
