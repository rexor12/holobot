from asyncpg.connection import Connection

from holobot.sdk.database import DatabaseManagerInterface
from holobot.sdk.database.queries import Query
from holobot.sdk.database.queries.enums import Equality
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none
from .ilog_settings_repository import ILogSettingsRepository

TABLE_NAME = "moderation_log_settings"

@injectable(ILogSettingsRepository)
class LogSettingsRepository(ILogSettingsRepository):
    def __init__(self, database_manager: DatabaseManagerInterface) -> None:
        super().__init__()
        self.__database_manager: DatabaseManagerInterface = database_manager

    async def get_log_channel(self, server_id: str) -> str | None:
        assert_not_none(server_id, "server_id")

        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                return await Query.select().from_table(TABLE_NAME).column(
                    "channel_id"
                ).where().field(
                    "server_id", Equality.EQUAL, server_id
                ).compile().fetchval(connection)

    async def set_log_channel(self, server_id: str, channel_id: str) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(channel_id, "channel_id")

        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                await Query.insert().in_table(TABLE_NAME).fields(
                    ("server_id", server_id),
                    ("channel_id", channel_id)
                ).on_conflict("server_id").update().field(
                    "channel_id", channel_id
                ).field(
                    "modified_at", "(NOW() AT TIME ZONE 'utc')", True
                ).compile().execute(connection)

    async def clear_log_channel(self, server_id: str) -> None:
        assert_not_none(server_id, "server_id")

        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                await Query.delete().from_table(TABLE_NAME).where().field(
                    "server_id", Equality.EQUAL, server_id
                ).compile().execute(connection)
