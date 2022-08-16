from .iwarn_settings_repository import IWarnSettingsRepository
from ..models import WarnSettings
from asyncpg.connection import Connection
from datetime import timedelta
from holobot.sdk.database import DatabaseManagerInterface
from holobot.sdk.database.queries import Query
from holobot.sdk.database.queries.enums import Equality
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none

TABLE_NAME = "moderation_warn_settings"

@injectable(IWarnSettingsRepository)
class WarnSettingsRepository(IWarnSettingsRepository):
    def __init__(self, database_manager: DatabaseManagerInterface) -> None:
        super().__init__()
        self.__database_manager: DatabaseManagerInterface = database_manager

    async def get_warn_decay_threshold(self, server_id: str) -> timedelta | None:
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
                ).field(
                    "modified_at", "(NOW() AT TIME ZONE 'utc')", True
                ).compile().execute(connection)

    async def clear_warn_decay_threshold(self, server_id: str) -> None:
        assert_not_none(server_id, "server_id")

        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                await Query.delete().from_table(TABLE_NAME).where().field(
                    "server_id", Equality.EQUAL, server_id
                ).compile().execute(connection)

    async def get_warn_settings(self, server_id: str) -> WarnSettings:
        assert_not_none(server_id, "server_id")

        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                record = await Query.select().from_table(TABLE_NAME).columns(
                    "auto_mute_after", "auto_mute_duration", "auto_kick_after", "auto_ban_after"
                ).where().field(
                    "server_id", Equality.EQUAL, server_id
                ).compile().fetchrow(connection)
                return WarnSettings(
                    auto_mute_after=record["auto_mute_after"],
                    auto_mute_duration=record["auto_mute_duration"],
                    auto_kick_after=record["auto_kick_after"],
                    auto_ban_after=record["auto_ban_after"]
                ) if record else WarnSettings()

    async def set_auto_mute(self, server_id: str, warn_count: int, duration: timedelta | None) -> None:
        assert_not_none(server_id, "server_id")

        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                await Query.insert().in_table(TABLE_NAME).fields(
                    ("server_id", server_id),
                    ("auto_mute_after", warn_count),
                    ("auto_mute_duration", duration)
                ).on_conflict("server_id").update().field(
                    "auto_mute_after", warn_count
                ).field(
                    "auto_mute_duration", duration
                ).field(
                    "modified_at", "(NOW() AT TIME ZONE 'utc')", True
                ).compile().execute(connection)

    async def set_auto_kick(self, server_id: str, warn_count: int) -> None:
        assert_not_none(server_id, "server_id")

        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                await Query.insert().in_table(TABLE_NAME).fields(
                    ("server_id", server_id),
                    ("auto_kick_after", warn_count)
                ).on_conflict("server_id").update().field(
                    "auto_kick_after", warn_count
                ).field(
                    "modified_at", "(NOW() AT TIME ZONE 'utc')", True
                ).compile().execute(connection)

    async def set_auto_ban(self, server_id: str, warn_count: int) -> None:
        assert_not_none(server_id, "server_id")

        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                await Query.insert().in_table(TABLE_NAME).fields(
                    ("server_id", server_id),
                    ("auto_ban_after", warn_count)
                ).on_conflict("server_id").update().field(
                    "auto_ban_after", warn_count
                ).field(
                    "modified_at", "(NOW() AT TIME ZONE 'utc')", True
                ).compile().execute(connection)
