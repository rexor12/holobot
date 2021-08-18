from .ipermission_repository import IPermissionRepository
from ..enums import ModeratorPermission
from asyncpg.connection import Connection
from holobot.sdk.database import DatabaseManagerInterface
from holobot.sdk.database.queries import Query
from holobot.sdk.database.queries.enums import Connector, Equality
from holobot.sdk.exceptions import ArgumentError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none

TABLE_NAME = "moderation_users"

@injectable(IPermissionRepository)
class PermissionRepository(IPermissionRepository):
    def __init__(self, database_manager: DatabaseManagerInterface) -> None:
        super().__init__()
        self.__database_manager: DatabaseManagerInterface = database_manager

    async def add_user_permissions(self, server_id: str, user_id: str, permissions: ModeratorPermission) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")
        # Sanitization because this argument is used as a raw value.
        if not isinstance(permissions, ModeratorPermission):
            raise ArgumentError("permissions", f"Expected ModeratorPermission but got {type(permissions)}.")

        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                await Query.insert().in_table(TABLE_NAME).fields(
                    ("server_id", server_id),
                    ("user_id", user_id),
                    ("permissions", permissions.value)
                ).on_conflict("server_id", "user_id").update().field(
                    "permissions", f"{TABLE_NAME}.permissions | {permissions.value}", True
                ).compile().execute(connection)
    
    async def remove_user_permissions(self, server_id: str, user_id: str, permissions: ModeratorPermission) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")
        # Sanitization because this argument is used as a raw value.
        if not isinstance(permissions, ModeratorPermission):
            raise ArgumentError("permissions", f"Expected ModeratorPermission but got {type(permissions)}.")

        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                await Query.update().table(TABLE_NAME).field(
                    "permissions", f"permissions # (permissions & {permissions.value})", True
                ).where().fields(
                    Connector.AND,
                    ("server_id", Equality.EQUAL, server_id),
                    ("user_id", Equality.EQUAL, user_id)
                ).compile().execute(connection)
    
    async def get_user_permissions(self, server_id: str, user_id: str) -> ModeratorPermission:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                permissions = await Query.select().from_table(TABLE_NAME).column(
                    "permissions"
                ).where().fields(
                    Connector.AND,
                    ("server_id", Equality.EQUAL, server_id),
                    ("user_id", Equality.EQUAL, user_id)
                ).compile().fetchval(connection)
                return ModeratorPermission(permissions) if permissions is not None else ModeratorPermission.NONE
