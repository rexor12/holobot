from holobot.extensions.mudada.models import (
    AggregatedRating, RatingMetadata, Valentine2025Rating, Valentine2025RatingId
)
from holobot.sdk.database import IDatabaseManager, IUnitOfWorkProvider
from holobot.sdk.database.entities import PrimaryKey
from holobot.sdk.database.queries import Query
from holobot.sdk.database.queries.enums import Connector, Equality, Order
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.queries import PaginationResult
from .ivalentine2025_rating_repository import IValentine2025RatingRepository
from .records import Valentine2025RatingRecord

@injectable(IValentine2025RatingRepository)
class Valentine2025RatingRepository(
    RepositoryBase[Valentine2025RatingId, Valentine2025RatingRecord, Valentine2025Rating],
    IValentine2025RatingRepository
):
    @property
    def record_type(self) -> type[Valentine2025RatingRecord]:
        return Valentine2025RatingRecord

    @property
    def model_type(self) -> type[Valentine2025Rating]:
        return Valentine2025Rating

    @property
    def identifier_type(self) -> type[Valentine2025RatingId]:
        return Valentine2025RatingId

    @property
    def table_name(self) -> str:
        return "valentine2025_ratings"

    @property
    def schema_name(self) -> str:
        return "mudada"

    def __init__(
        self,
        database_manager: IDatabaseManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__(database_manager, unit_of_work_provider)

    async def get_aggregated_data(
        self,
        user_id: int
    ) -> AggregatedRating | None:
        async with (session := await self._get_session()):
            result = await session.connection.fetchrow(
                (
                    "SELECT "
                    " AVG(score1) AS avg_score1, AVG(score2) AS avg_score2, AVG(score3) AS avg_score3,"
                    " AVG(score4) AS avg_score4, AVG(score5) AS avg_score5, AVG(score6) AS avg_score6"
                    f" FROM {self.schema_name}.{self.table_name}"
                    " WHERE target_user_id = $1 AND is_deleted = false"
                ),
                user_id
            )
            if not result or result["avg_score1"] is None:
                return None

            return AggregatedRating(
                average_score1=float(result["avg_score1"]),
                average_score2=float(result["avg_score2"]),
                average_score3=float(result["avg_score3"]),
                average_score4=float(result["avg_score4"]),
                average_score5=float(result["avg_score5"]),
                average_score6=float(result["avg_score6"])
            )

    async def paginate_ratings(
        self,
        target_user_id: int,
        page_index: int,
        page_size: int
    ) -> PaginationResult[RatingMetadata]:
        async with (session := await self._get_session()):
            query = (Query
                .select()
                .column("source_user_id")
                .from_table(self.table_name, None, self.schema_name)
                .where()
                .fields(
                    Connector.AND,
                    ("target_user_id", Equality.EQUAL, target_user_id),
                    ("is_deleted", Equality.EQUAL, False)
                )
            )

            result = await query.paginate(
                (("source_user_id", Order.ASCENDING),),
                page_index,
                page_size
            ).compile().fetch(session.connection)

            return PaginationResult[RatingMetadata](
                result.page_index,
                result.page_size,
                result.total_count,
                [
                    RatingMetadata(
                        source_user_id=record["source_user_id"]
                    )
                    for record in result.records
                ]
            )

    def _map_record_to_model(self, record: Valentine2025RatingRecord) -> Valentine2025Rating:
        return Valentine2025Rating(
            identifier=Valentine2025RatingId(
                source_user_id=record.source_user_id.value,
                target_user_id=record.target_user_id.value
            ),
            score1=record.score1,
            score2=record.score2,
            score3=record.score3,
            score4=record.score4,
            score5=record.score5,
            score6=record.score6,
            message=record.message,
            is_deleted=record.is_deleted
        )

    def _map_model_to_record(self, model: Valentine2025Rating) -> Valentine2025RatingRecord:
        return Valentine2025RatingRecord(
            source_user_id=PrimaryKey(model.identifier.source_user_id),
            target_user_id=PrimaryKey(model.identifier.target_user_id),
            score1=model.score1,
            score2=model.score2,
            score3=model.score3,
            score4=model.score4,
            score5=model.score5,
            score6=model.score6,
            message=model.message,
            is_deleted=model.is_deleted
        )
