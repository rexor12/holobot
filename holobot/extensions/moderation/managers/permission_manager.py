from .ipermission_manager import IPermissionManager
from ..enums import ModeratorPermission
from ..repositories import IPermissionRepository
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none

@injectable(IPermissionManager)
class PermissionManager(IPermissionManager):
    def __init__(self, repository: IPermissionRepository) -> None:
        super().__init__()
        self.__repository: IPermissionRepository = repository

    async def add_permissions(self, server_id: str, user_id: str, permissions: ModeratorPermission) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        await self.__repository.add_user_permissions(server_id, user_id, permissions)
    
    async def remove_permissions(self, server_id: str, user_id: str, permissions: ModeratorPermission) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        await self.__repository.remove_user_permissions(server_id, user_id, permissions)
