from .iwarn_repository import IWarnRepository
from ..models import WarnStrike
from asyncpg.connection import Connection
from datetime import timedelta
from holobot.sdk.database import DatabaseManagerInterface
from holobot.sdk.database.queries import Query
from holobot.sdk.database.queries.enums import Connector, Equality
from holobot.sdk.exceptions import ArgumentError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none
from typing import Optional, Tuple

TABLE_NAME = "moderation_warns"

@injectable(IWarnRepository)
class WarnRepository(IWarnRepository):
    def __init__(self, database_manager: DatabaseManagerInterface) -> None:
        super().__init__()
        self.__database_manager: DatabaseManagerInterface = database_manager

    async def get_warns_by_user(self, server_id: str, user_id: str, start_offset: int, max_count: int) -> Tuple[WarnStrike, ...]:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                records = await Query.select().from_table(TABLE_NAME).columns(
                    "id, created_at, server_id, user_id, reason, warner_id"
                ).where().fields(
                    Connector.AND,
                    ("server_id", Equality.EQUAL, server_id),
                    ("user_id", Equality.EQUAL, user_id)
                ).limit().start_index(start_offset).max_count(max_count).compile().fetch(connection)
                return tuple([WarnRepository.__map_to_model(record) for record in records])

    async def add_warn(self, warn_strike: WarnStrike) -> int:
        assert_not_none(warn_strike, "warn_strike")
        assert_not_none(warn_strike.server_id, "warn_strike.server_id")
        assert_not_none(warn_strike.user_id, "warn_strike.user_id")
        assert_not_none(warn_strike.reason, "warn_strike.reason")
        assert_not_none(warn_strike.warner_id, "warn_strike.warner_id")
        if warn_strike.id != -1:
            raise ArgumentError("warn_strike", "This warn strike has been added already.")

        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                id: Optional[int] = await Query.insert().in_table(TABLE_NAME).fields(
                    ("server_id", warn_strike.server_id),
                    ("user_id", warn_strike.user_id),
                    ("reason", warn_strike.reason),
                    ("warner_id", warn_strike.warner_id)
                ).returning().column("id").compile().fetchval(connection)
                if id is None:
                    raise ValueError("Unexpected error while creating a new warn.")
                return id
    
    async def clear_warns_by_server(self, server_id: str) -> None:
        assert_not_none(server_id, "server_id")

        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                await Query.delete().from_table(TABLE_NAME).where().field(
                    "server_id", Equality.EQUAL, server_id
                ).compile().execute(connection)
    
    async def clear_warns_by_user(self, server_id: str, user_id: str) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                await Query.delete().from_table(TABLE_NAME).where().fields(
                    Connector.AND,
                    ("server_id", Equality.EQUAL, server_id),
                    ("user_id", Equality.EQUAL, user_id)
                ).compile().execute(connection)
    
    async def clear_warns_older_than(self, elapsed: timedelta) -> None:
        # Sanitization because this argument is used as a raw value.
        if not isinstance(elapsed, timedelta):
            raise ArgumentError("elapsed", f"Expected timedelta but got {type(elapsed)}.")

        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                await Query.delete().from_table(TABLE_NAME).where().field(
                    "created_at", Equality.LESS, f"created_at + interval '{int(elapsed.total_seconds())} seconds'", True
                ).compile().execute(connection)
    
    @staticmethod
    def __map_to_model(record) -> WarnStrike:
        model = WarnStrike()
        model.id = record["id"]
        model.created_at = record["created_at"]
        model.server_id = record["server_id"]
        model.user_id = record["user_id"]
        model.reason = record["reason"]
        model.warner_id = record["warner_id"]
        return model
