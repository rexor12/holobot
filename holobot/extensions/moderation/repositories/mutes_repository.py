from .imutes_repository import IMutesRepository
from ..models import Mute
from asyncpg.connection import Connection
from datetime import datetime
from holobot.sdk.database import DatabaseManagerInterface
from holobot.sdk.database.queries import Query
from holobot.sdk.database.queries.enums import Connector, Equality
from holobot.sdk.database.statuses import CommandComplete
from holobot.sdk.database.statuses.command_tags import DeleteCommandTag
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none

TABLE_NAME = "moderation_mutes"

@injectable(IMutesRepository)
class MutesRepository(IMutesRepository):
    def __init__(self, database_manager: DatabaseManagerInterface) -> None:
        super().__init__()
        self.__database_manager: DatabaseManagerInterface = database_manager

    async def get_mute(self, server_id: str, user_id: str) -> datetime | None:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                return await Query.select().column(
                    "expires_at"
                ).from_table(TABLE_NAME).where().fields(
                    Connector.AND,
                    ("server_id", Equality.EQUAL, server_id),
                    ("user_id", Equality.EQUAL, user_id)
                ).compile().fetchval(connection)

    async def upsert_mute(self, server_id: str, user_id: str, expires_at: datetime) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                await Query.insert().in_table(TABLE_NAME).fields(
                    ("server_id", server_id),
                    ("user_id", user_id),
                    ("expires_at", expires_at)
                ).on_conflict("server_id", "user_id").update().field(
                    "expires_at", expires_at
                ).field(
                    "modified_at", "(NOW() AT TIME ZONE 'utc')", True
                ).compile().execute(connection)

    async def delete_mute(self, server_id: str, user_id: str) -> int:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                status: CommandComplete[DeleteCommandTag] = await Query.delete().from_table(TABLE_NAME).where().fields(
                    Connector.AND,
                    ("server_id", Equality.EQUAL, server_id),
                    ("user_id", Equality.EQUAL, user_id)
                ).compile().execute(connection)

                return status.command_tag.rows

    async def delete_expired_mutes(self) -> tuple[Mute, ...]:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                records = await Query.delete().from_table(TABLE_NAME).where().field(
                    "expires_at", Equality.LESS, "(NOW() at time zone 'utc')", True
                ).returning().columns(
                    "server_id", "user_id"
                ).compile().fetch(connection)

                return tuple([
                    Mute(
                        server_id=record["server_id"],
                        user_id=record["user_id"]
                    ) for record in records
                ])
