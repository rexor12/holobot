from holobot.extensions.moderation.enums import ModeratorPermission
from holobot.extensions.moderation.models import User
from holobot.extensions.moderation.repositories import IUserRepository
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none
from .ipermission_manager import IPermissionManager

@injectable(IPermissionManager)
class PermissionManager(IPermissionManager):
    def __init__(self, repository: IUserRepository) -> None:
        super().__init__()
        self.__repository: IUserRepository = repository

    async def add_permissions(self, server_id: str, user_id: str, permissions: ModeratorPermission) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        if permissions is ModeratorPermission.NONE:
            return

        user = await self.__repository.get_by_server(server_id, user_id)
        if user:
            user.permissions |= permissions
            await self.__repository.update(user)
            return

        user = User(
            server_id=server_id,
            user_id=user_id,
            permissions=permissions
        )
        await self.__repository.add(user)

    async def remove_permissions(self, server_id: str, user_id: str, permissions: ModeratorPermission) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        if permissions is ModeratorPermission.NONE:
            return

        user = await self.__repository.get_by_server(server_id, user_id)
        if not user:
            return

        user.permissions ^= permissions
        await self.__repository.update(user)

    async def remove_all_permissions(
        self,
        server_id: str,
        user_id: str
    ) -> bool:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        user = await self.__repository.get_by_server(server_id, user_id)
        if not user:
            return False

        had_permissions = user.permissions is not ModeratorPermission.NONE
        user.permissions = ModeratorPermission.NONE
        await self.__repository.update(user)

        return had_permissions

    async def has_permissions(self, server_id: str, user_id: str, permissions: ModeratorPermission) -> bool:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        if permissions is ModeratorPermission.NONE:
            return True

        user = await self.__repository.get_by_server(server_id, user_id)
        return permissions in user.permissions if user else False
