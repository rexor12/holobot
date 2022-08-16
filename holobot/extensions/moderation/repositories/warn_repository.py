from datetime import timedelta

from asyncpg.connection import Connection

from .iwarn_repository import IWarnRepository
from ..models import WarnStrike
from holobot.sdk.database import DatabaseManagerInterface
from holobot.sdk.database.queries import Query
from holobot.sdk.database.queries.constraints import and_expression, column_expression, or_expression
from holobot.sdk.database.queries.enums import Connector, Equality
from holobot.sdk.database.statuses import CommandComplete
from holobot.sdk.database.statuses.command_tags import DeleteCommandTag
from holobot.sdk.exceptions import ArgumentError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.queries import PaginationResult
from holobot.sdk.utils import assert_not_none

TABLE_NAME = "moderation_warns"
SETTINGS_TABLE_NAME = "moderation_warn_settings"

@injectable(IWarnRepository)
class WarnRepository(IWarnRepository):
    def __init__(self, database_manager: DatabaseManagerInterface) -> None:
        super().__init__()
        self.__database_manager: DatabaseManagerInterface = database_manager

    async def get_warn_count_by_user(self, server_id: str, user_id: str) -> int:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                count: int | None = await connection.fetchval(
                    (
                        f"SELECT COUNT(*) FROM {TABLE_NAME} AS t1"
                        f" LEFT JOIN {SETTINGS_TABLE_NAME} AS t2 ON t1.server_id = t2.server_id"
                        " WHERE (t2.decay_threshold IS NULL OR (t1.created_at >= (NOW() at time zone 'utc') - t2.decay_threshold))"
                        " AND t1.server_id = $1 AND t1.user_id = $2"
                    ), server_id, user_id
                )
                return count if count is not None else 0

    async def get_warns_by_user(
        self,
        server_id: str,
        user_id: str,
        page_index: int,
        max_count: int
    ) -> PaginationResult[WarnStrike]:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                result = await (Query
                    .select()
                    .columns("t1.id", "t1.created_at", "t1.server_id", "t1.user_id", "t1.reason", "t1.warner_id")
                    .from_table(TABLE_NAME, "t1")
                    .join(SETTINGS_TABLE_NAME, "t1.server_id", "t2.server_id", "t2")
                    .where()
                    .expression(
                        and_expression(
                            or_expression(
                                column_expression("t2.decay_threshold", Equality.EQUAL, None),
                                column_expression("t1.created_at", Equality.GREATER | Equality.EQUAL, "((NOW() at time zone 'utc') - t2.decay_threshold)", True)
                            ),
                            column_expression("t1.server_id", Equality.EQUAL, server_id),
                            column_expression("t1.user_id", Equality.EQUAL, user_id)
                        )
                    )
                    .paginate("t1.id", page_index, max_count)
                    .compile()
                    .fetch(connection)
                )

                return PaginationResult(
                    result.page_index,
                    result.page_size,
                    result.total_count,
                    [WarnRepository.__map_to_model(record) for record in result.records]
                )

    async def add_warn(self, warn_strike: WarnStrike, decay_threshold: timedelta | None = None) -> int:
        assert_not_none(warn_strike, "warn_strike")
        assert_not_none(warn_strike.server_id, "warn_strike.server_id")
        assert_not_none(warn_strike.user_id, "warn_strike.user_id")
        assert_not_none(warn_strike.reason, "warn_strike.reason")
        assert_not_none(warn_strike.warner_id, "warn_strike.warner_id")
        if warn_strike.id != -1:
            raise ArgumentError("warn_strike", "This warn strike has been added already.")
        # Sanitization because this argument is used as a raw value.
        if decay_threshold is not None and not isinstance(decay_threshold, timedelta):
            raise ArgumentError("decay_threshold", f"Expected timedelta but got {type(decay_threshold)}.")

        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                await self.__clear_warns_older_than(connection, decay_threshold)
                id: int | None = await Query.insert().in_table(TABLE_NAME).fields(
                    ("server_id", warn_strike.server_id),
                    ("user_id", warn_strike.user_id),
                    ("reason", warn_strike.reason),
                    ("warner_id", warn_strike.warner_id)
                ).returning().column("id").compile().fetchval(connection)
                if id is None:
                    raise ValueError("Unexpected error while creating a new warn.")
                return id

    async def clear_warns_by_server(self, server_id: str) -> int:
        assert_not_none(server_id, "server_id")

        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                status: CommandComplete[DeleteCommandTag] = await Query.delete().from_table(TABLE_NAME).where().field(
                    "server_id", Equality.EQUAL, server_id
                ).compile().execute(connection)
                return status.command_tag.rows

    async def clear_warns_by_user(self, server_id: str, user_id: str) -> int:
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

    async def clear_expired_warns(self) -> int:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                status = await connection.execute(
                    (
                        f"DELETE FROM {TABLE_NAME} AS t1"
                        f" USING {SETTINGS_TABLE_NAME} AS t2"
                        " WHERE t1.server_id = t2.server_id AND t2.decay_threshold IS NOT NULL AND t1.created_at < (NOW() at time zone 'utc') - t2.decay_threshold"
                    )
                )
                status_tag: CommandComplete[DeleteCommandTag] = CommandComplete.parse(status)
                return status_tag.command_tag.rows

    async def __clear_warns_older_than(self, connection: Connection, threshold: timedelta | None) -> None:
        if threshold is None:
            return

        await Query.delete().from_table(TABLE_NAME).where().field(
            "created_at", Equality.LESS, f"(NOW() at time zone 'utc') - interval '{int(threshold.total_seconds())} seconds'", True
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
