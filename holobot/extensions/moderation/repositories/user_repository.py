from asyncpg.connection import Connection

from holobot.extensions.moderation.models import User
from holobot.sdk.database import IDatabaseManager
from holobot.sdk.database.queries import Query
from holobot.sdk.database.queries.enums import Connector, Equality
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none
from .iuser_repository import IUserRepository
from .records import UserRecord

@injectable(IUserRepository)
class UserRepository(
    RepositoryBase[int, UserRecord, User],
    IUserRepository
):
    @property
    def record_type(self) -> type[UserRecord]:
        return UserRecord

    @property
    def table_name(self) -> str:
        return "moderation_users"

    def __init__(self, database_manager: IDatabaseManager) -> None:
        super().__init__(database_manager)

    async def get_by_server(
        self,
        server_id: str,
        user_id: str
    ) -> User | None:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        return await self._get_by_filter(lambda where: (
            where.fields(
                Connector.AND,
                ("server_id", Equality.EQUAL, server_id),
                ("user_id", Equality.EQUAL, user_id)
            )
        ))

    async def delete_by_server(
        self,
        server_id: str,
        user_id: str
    ) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        async with self._database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                await (Query
                    .delete()
                    .from_table(self.table_name)
                    .where()
                    .fields(
                        Connector.AND,
                        ("server_id", Equality.EQUAL, server_id),
                        ("user_id", Equality.EQUAL, user_id)
                    )
                    .compile()
                    .execute(connection)
                )

    def _map_record_to_model(self, record: UserRecord) -> User:
        return User(
            identifier=record.id,
            created_at=record.created_at,
            permissions=record.permissions,
            server_id=record.server_id,
            user_id=record.user_id
        )

    def _map_model_to_record(self, model: User) -> UserRecord:
        return UserRecord(
            id=model.identifier,
            created_at=model.created_at,
            permissions=model.permissions,
            server_id=model.server_id,
            user_id=model.user_id
        )
