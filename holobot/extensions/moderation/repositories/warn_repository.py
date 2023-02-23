from collections.abc import Awaitable
from datetime import timedelta

from asyncpg.connection import Connection

from holobot.extensions.moderation.models import WarnStrike
from holobot.sdk.database import IDatabaseManager, IUnitOfWorkProvider
from holobot.sdk.database.queries import Query
from holobot.sdk.database.queries.constraints import (
    and_expression, column_expression, or_expression
)
from holobot.sdk.database.queries.enums import Connector, Equality, Order
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.database.statuses import CommandComplete
from holobot.sdk.database.statuses.command_tags import DeleteCommandTag
from holobot.sdk.exceptions import ArgumentError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.queries import PaginationResult
from holobot.sdk.utils import assert_not_none
from .iwarn_repository import IWarnRepository
from .records import WarnStrikeRecord

_SETTINGS_TABLE_NAME = "moderation_warn_settings"

@injectable(IWarnRepository)
class WarnRepository(
    RepositoryBase[int, WarnStrikeRecord, WarnStrike],
    IWarnRepository
):
    @property
    def record_type(self) -> type[WarnStrikeRecord]:
        return WarnStrikeRecord

    @property
    def model_type(self) -> type[WarnStrike]:
        return WarnStrike

    @property
    def table_name(self) -> str:
        return "moderation_warns"

    def __init__(
        self,
        database_manager: IDatabaseManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__(database_manager, unit_of_work_provider)

    async def get_warn_count_by_user(self, server_id: str, user_id: str) -> int:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        async with (session := await self._get_session()):
            count: int | None = await session.connection.fetchval(
                (
                    f"SELECT COUNT(*) FROM {self.table_name} AS t1"
                    f" LEFT JOIN {_SETTINGS_TABLE_NAME} AS t2 ON t1.server_id = t2.server_id"
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

        async with (session := await self._get_session()):
            result = await (Query
                .select()
                .columns("t1.id", "t1.created_at", "t1.server_id", "t1.user_id", "t1.reason", "t1.warner_id")
                .from_table(self.table_name, "t1")
                .join(_SETTINGS_TABLE_NAME, "t1.server_id", "t2.server_id", "t2")
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
                .paginate((("t1.id", Order.ASCENDING),), page_index, max_count)
                .compile()
                .fetch(session.connection)
            )

            return PaginationResult(
                result.page_index,
                result.page_size,
                result.total_count,
                [
                    self._map_record_to_model(self._map_query_result_to_record(record))
                    for record in result.records
                ]
            )

    async def add_warn(
        self,
        warn_strike: WarnStrike,
        decay_threshold: timedelta | None = None
    ) -> int:
        assert_not_none(warn_strike, "warn_strike")
        assert_not_none(warn_strike.server_id, "warn_strike.server_id")
        assert_not_none(warn_strike.user_id, "warn_strike.user_id")
        assert_not_none(warn_strike.reason, "warn_strike.reason")
        assert_not_none(warn_strike.warner_id, "warn_strike.warner_id")
        if warn_strike.identifier != -1:
            raise ArgumentError("warn_strike", "This warn strike has been added already.")
        # Sanitization because this argument is used as a raw value.
        if decay_threshold is not None and not isinstance(decay_threshold, timedelta):
            raise ArgumentError("decay_threshold", f"Expected timedelta but got {type(decay_threshold)}.")

        async with (session := await self._get_session()):
            await self.__clear_warns_older_than(session.connection, decay_threshold)
            id: int | None = await Query.insert().in_table(self.table_name).fields(
                ("server_id", warn_strike.server_id),
                ("user_id", warn_strike.user_id),
                ("reason", warn_strike.reason),
                ("warner_id", warn_strike.warner_id)
            ).returning().column("id").compile().fetchval(session.connection)
            if id is None:
                raise ValueError("Unexpected error while creating a new warn.")
            return id

    def clear_warns_by_server(self, server_id: str) -> Awaitable[int]:
        assert_not_none(server_id, "server_id")

        return self._delete_by_filter(
            lambda where: where.field("server_id", Equality.EQUAL, server_id)
        )

    def clear_warns_by_user(self, server_id: str, user_id: str) -> Awaitable[int]:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        return self._delete_by_filter(
            lambda where: where.fields(
                Connector.AND,
                ("server_id", Equality.EQUAL, server_id),
                ("user_id", Equality.EQUAL, user_id)
            )
        )

    async def clear_expired_warns(self) -> int:
        async with (session := await self._get_session()):
            status = await session.connection.execute(
                (
                    f"DELETE FROM {self.table_name} AS t1"
                    f" USING {_SETTINGS_TABLE_NAME} AS t2"
                    " WHERE t1.server_id = t2.server_id AND t2.decay_threshold IS NOT NULL AND t1.created_at < (NOW() at time zone 'utc') - t2.decay_threshold"
                )
            )
            status_tag: CommandComplete[DeleteCommandTag] = CommandComplete.parse(status)
            return status_tag.command_tag.rows

    async def __clear_warns_older_than(self, connection: Connection, threshold: timedelta | None) -> None:
        if threshold is None:
            return

        await Query.delete().from_table(self.table_name).where().field(
            "created_at", Equality.LESS, f"(NOW() at time zone 'utc') - interval '{int(threshold.total_seconds())} seconds'", True
        ).compile().execute(connection)

    def _map_record_to_model(self, record: WarnStrikeRecord) -> WarnStrike:
        return WarnStrike(
            identifier=record.id,
            created_at=record.created_at,
            server_id=record.server_id,
            user_id=record.user_id,
            reason=record.reason,
            warner_id=record.warner_id
        )

    def _map_model_to_record(self, model: WarnStrike) -> WarnStrikeRecord:
        return WarnStrikeRecord(
            id=model.identifier,
            created_at=model.created_at,
            server_id=model.server_id,
            user_id=model.user_id,
            reason=model.reason,
            warner_id=model.warner_id
        )
