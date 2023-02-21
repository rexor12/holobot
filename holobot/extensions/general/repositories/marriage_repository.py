from collections.abc import Awaitable
from datetime import datetime, timezone
from typing import cast

from holobot.extensions.general.enums import RankingType
from holobot.extensions.general.models import Marriage, RankingInfo
from holobot.sdk.database import IDatabaseManager, IUnitOfWorkProvider
from holobot.sdk.database.queries import Query
from holobot.sdk.database.queries.constraints import (
    and_expression, column_expression, or_expression
)
from holobot.sdk.database.queries.enums import Equality, Order
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.queries import PaginationResult
from holobot.sdk.utils import assert_not_none
from holobot.sdk.utils.datetime_utils import set_time_zone
from .imarriage_repository import IMarriageRepository
from .records import MarriageRecord

@injectable(IMarriageRepository)
class MarriageRepository(
    RepositoryBase[str, MarriageRecord, Marriage],
    IMarriageRepository
):
    @property
    def record_type(self) -> type[MarriageRecord]:
        return MarriageRecord

    @property
    def model_type(self) -> type[Marriage]:
        return Marriage

    @property
    def table_name(self) -> str:
        return "marriages"

    def __init__(
        self,
        database_manager: IDatabaseManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__(database_manager, unit_of_work_provider)

    def get_by_user(
        self,
        server_id: str,
        user_id: str
    ) -> Awaitable[Marriage | None]:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        return self._get_by_filter(lambda where: (
            where.expression(
                and_expression(
                    column_expression("server_id", Equality.EQUAL, server_id),
                    or_expression(
                        column_expression("user_id1", Equality.EQUAL, user_id),
                        column_expression("user_id2", Equality.EQUAL, user_id)
                    )
                )
            )
        ))

    def get_by_users(
        self,
        server_id: str,
        user_id1: str,
        user_id2: str
    ) -> Awaitable[Marriage | None]:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id1, "user_id1")
        assert_not_none(user_id2, "user_id2")

        return self._get_by_filter(lambda where: (
            where.expression(
                and_expression(
                    column_expression("server_id", Equality.EQUAL, server_id),
                    or_expression(
                        and_expression(
                            column_expression("user_id1", Equality.EQUAL, user_id1),
                            column_expression("user_id2", Equality.EQUAL, user_id2)
                        ),
                        and_expression(
                            column_expression("user_id1", Equality.EQUAL, user_id2),
                            column_expression("user_id2", Equality.EQUAL, user_id1)
                        ),
                    )
                )
            )
        ))

    async def delete_by_user(
        self,
        server_id: str,
        user_id1: str,
        user_id2: str
    ) -> bool:
        result = await self._delete_by_filter(
            lambda where: where.expression(
                and_expression(
                    column_expression("server_id", Equality.EQUAL, server_id),
                    or_expression(
                        and_expression(
                            column_expression("user_id1", Equality.EQUAL, user_id1),
                            column_expression("user_id2", Equality.EQUAL, user_id2)
                        ),
                        and_expression(
                            column_expression("user_id1", Equality.EQUAL, user_id2),
                            column_expression("user_id2", Equality.EQUAL, user_id1)
                        )
                    )
                )
            )
        )

        return result > 0

    async def paginate_rankings(
        self,
        server_id: str,
        ranking_type: RankingType,
        page_index: int,
        page_size: int
    ) -> PaginationResult[RankingInfo]:
        columns = set[str](("user_id1", "user_id2", "level", "married_at"))
        ordering_columns = MarriageRepository.__get_ranking_ordering_columns(ranking_type)
        for ordering_column, _ in ordering_columns:
            columns.add(ordering_column)

        async with (session := await self._get_session()):
            result = await (Query
                .select()
                .columns(*columns)
                .from_table(self.table_name)
                .where()
                .field("server_id", Equality.EQUAL, server_id)
                .paginate(ordering_columns, page_index, page_size)
                .compile().fetch(session.connection)
            )

            return PaginationResult[RankingInfo](
                result.page_index,
                result.page_size,
                result.total_count,
                [
                    RankingInfo(
                        user_id1=record["user_id1"],
                        user_id2=record["user_id2"],
                        level=record["level"],
                        married_at=set_time_zone(cast(datetime, record["married_at"]), timezone.utc)
                    )
                    for record in result.records
                ]
            )

    def _map_record_to_model(self, record: MarriageRecord) -> Marriage:
        return Marriage(
            identifier=record.id,
            server_id=record.server_id,
            user_id1=record.user_id1,
            user_id2=record.user_id2,
            married_at=record.married_at,
            level=record.level,
            last_level_up_at=record.last_level_up_at,
            exp_points=record.exp_points,
            last_activity_at=record.last_activity_at,
            activity_tier_reset_at=record.activity_tier_reset_at,
            activity_tier=record.activity_tier,
            hug_count=record.hug_count,
            kiss_count=record.kiss_count,
            pat_count=record.pat_count,
            poke_count=record.poke_count,
            match_bonus=record.match_bonus
        )

    def _map_model_to_record(self, model: Marriage) -> MarriageRecord:
        return MarriageRecord(
            id=model.identifier,
            server_id=model.server_id,
            user_id1=model.user_id1,
            user_id2=model.user_id2,
            married_at=model.married_at,
            level=model.level,
            last_level_up_at=model.last_level_up_at,
            exp_points=model.exp_points,
            last_activity_at=model.last_activity_at,
            activity_tier_reset_at=model.activity_tier_reset_at,
            activity_tier=model.activity_tier,
            hug_count=model.hug_count,
            kiss_count=model.kiss_count,
            pat_count=model.pat_count,
            poke_count=model.poke_count,
            match_bonus=model.match_bonus
        )

    @staticmethod
    def __get_ranking_ordering_columns(
        ranking_type: RankingType
    ) -> tuple[tuple[str, Order], ...]:
        match ranking_type:
            case RankingType.LEVEL:
                return (("level", Order.DESCENDING), ("last_level_up_at", Order.ASCENDING))
            case _:
                return (("married_at", Order.ASCENDING),)
