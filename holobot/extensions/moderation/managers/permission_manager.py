from .ipermission_manager import IPermissionManager
from ..enums import ModeratorPermission
from ..repositories import IPermissionRepository
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none

# TODO Strip permissions when a user is kicked/banned or leaves the server.
# Transform discord.py events into listener events?
@injectable(IPermissionManager)
class PermissionManager(IPermissionManager):
    def __init__(self, repository: IPermissionRepository) -> None:
        super().__init__()
        self.__repository: IPermissionRepository = repository

    async def add_permissions(self, server_id: str, user_id: str, permissions: ModeratorPermission) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        if permissions == ModeratorPermission.NONE_USERS:
            return

        await self.__repository.add_user_permissions(server_id, user_id, permissions)
    
    async def remove_permissions(self, server_id: str, user_id: str, permissions: ModeratorPermission) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        if permissions == ModeratorPermission.NONE_USERS:
            return

        await self.__repository.remove_user_permissions(server_id, user_id, permissions)
    
    async def has_permissions(self, server_id: str, user_id: str, permissions: ModeratorPermission) -> bool:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        if permissions == ModeratorPermission.NONE_USERS:
            return True
        
        owned_permissions = await self.__repository.get_user_permissions(server_id, user_id)
        return permissions in owned_permissions
