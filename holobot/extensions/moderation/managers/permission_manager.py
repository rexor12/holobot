from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none
from ..enums import ModeratorPermission
from ..repositories import IPermissionRepository
from .ipermission_manager import IPermissionManager

@injectable(IPermissionManager)
class PermissionManager(IPermissionManager):
    def __init__(self, repository: IPermissionRepository) -> None:
        super().__init__()
        self.__repository: IPermissionRepository = repository

    async def add_permissions(self, server_id: str, user_id: str, permissions: ModeratorPermission) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        if permissions == ModeratorPermission.NONE:
            return

        await self.__repository.add_user_permissions(server_id, user_id, permissions)
    
    async def remove_permissions(self, server_id: str, user_id: str, permissions: ModeratorPermission) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        if permissions == ModeratorPermission.NONE:
            return

        await self.__repository.remove_user_permissions(server_id, user_id, permissions)

    async def remove_all_permissions(
        self,
        server_id: str,
        user_id: str
    ) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        await self.__repository.remove_user_permissions(
            server_id,
            user_id,
            ModeratorPermission.all_permissions()
        )
    
    async def has_permissions(self, server_id: str, user_id: str, permissions: ModeratorPermission) -> bool:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        if permissions == ModeratorPermission.NONE:
            return True
        
        owned_permissions = await self.__repository.get_user_permissions(server_id, user_id)
        return permissions in owned_permissions
