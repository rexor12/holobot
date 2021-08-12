from .iwarn_settings_repository import IWarnSettingsRepository
from asyncpg.connection import Connection
from datetime import timedelta
from holobot.sdk.database import DatabaseManagerInterface
from holobot.sdk.database.queries import Query
from holobot.sdk.database.queries.enums import Equality
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none
from typing import Optional

TABLE_NAME = "moderation_warn_settings"

@injectable(IWarnSettingsRepository)
class WarnSettingsRepository(IWarnSettingsRepository):
    def __init__(self, database_manager: DatabaseManagerInterface) -> None:
        super().__init__()
        self.__database_manager: DatabaseManagerInterface = database_manager

    async def get_warn_decay_threshold(self, server_id: str) -> Optional[timedelta]:
        assert_not_none(server_id, "server_id")

        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                return await Query.select().from_table(TABLE_NAME).column(
                    "decay_threshold"
                ).where().field(
                    "server_id", Equality.EQUAL, server_id
                ).compile().fetchval(connection)

    async def set_warn_decay_threshold(self, server_id: str, threshold: timedelta) -> None:
        assert_not_none(server_id, "server_id")

        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                await Query.insert().in_table(TABLE_NAME).fields(
                    ("server_id", server_id),
                    ("decay_threshold", threshold)
                ).on_conflict("server_id").update().field(
                    "decay_threshold", threshold
                ).compile().execute(connection)

    async def clear_warn_decay_threshold(self, server_id: str) -> None:
        assert_not_none(server_id, "server_id")

        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                await Query.delete().from_table(TABLE_NAME).where().field(
                    "server_id", Equality.EQUAL, server_id
                ).compile().execute(connection)
