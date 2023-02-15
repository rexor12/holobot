from asyncpg.connection import Connection

from holobot.extensions.giveaways.models import ExternalGiveawayItem, ExternalGiveawayItemMetadata
from holobot.sdk.database import IDatabaseManager, IUnitOfWorkProvider
from holobot.sdk.database.queries import Query, WhereBuilder, WhereConstraintBuilder
from holobot.sdk.database.queries.enums import Equality
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.database.statuses import CommandComplete
from holobot.sdk.database.statuses.command_tags import DeleteCommandTag
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.queries import PaginationResult
from .iexternal_giveaway_item_repository import IExternalGiveawayItemRepository
from .records import ExternalGiveawayItemRecord

@injectable(IExternalGiveawayItemRepository)
class ExternalGiveawayItemRepository(
    RepositoryBase[int, ExternalGiveawayItemRecord, ExternalGiveawayItem],
    IExternalGiveawayItemRepository
):
    @property
    def record_type(self) -> type[ExternalGiveawayItemRecord]:
        return ExternalGiveawayItemRecord

    @property
    def model_type(self) -> type[ExternalGiveawayItem]:
        return ExternalGiveawayItem

    @property
    def table_name(self) -> str:
        return "external_giveaway_items"

    def __init__(
        self,
        database_manager: IDatabaseManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__(database_manager, unit_of_work_provider)

    async def get_many(
        self,
        page_index: int,
        page_size: int,
        item_type: str,
        active_only: bool = True
    ) -> PaginationResult[ExternalGiveawayItem]:
        def get_filter(where: WhereBuilder) -> WhereConstraintBuilder:
            builder = where.field("item_type", Equality.EQUAL, item_type)
            if active_only:
                builder = builder.and_field(
                        "end_time", Equality.GREATER, "(NOW() AT TIME ZONE 'utc')", True
                    )
            return builder

        return await self._paginate(
            "id",
            page_index,
            page_size,
            get_filter
        )

    async def get_metadatas(
        self,
        page_index: int,
        page_size: int,
        item_type: str,
        active_only: bool = True
    ) -> PaginationResult[ExternalGiveawayItemMetadata]:
        async with self._database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                query = (Query
                    .select()
                    .columns("id", "title")
                    .from_table(self.table_name)
                    .where()
                    .field("item_type", Equality.EQUAL, item_type)
                )
                if active_only:
                    query = query.and_field(
                        "end_time", Equality.GREATER, "(NOW() AT TIME ZONE 'utc')", True
                    )
                result = await query.paginate("id", page_index, page_size).compile().fetch(connection)
                return PaginationResult(
                    result.page_index,
                    result.page_size,
                    result.total_count,
                    [
                        ExternalGiveawayItemMetadata(
                            identifier=record["id"],
                            title=record["title"]
                        )
                        for record in result.records
                    ]
                )

    async def exists(self, url: str, active_only: bool = True) -> bool:
        async with self._database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                query = (Query
                    .select()
                    .columns("id")
                    .from_table(self.table_name)
                    .where()
                    .field("url", Equality.EQUAL, url)
                )
                if active_only:
                    query = query.and_field(
                        "end_time", Equality.GREATER, "(NOW() AT TIME ZONE 'utc')", True
                    )
                return bool(await query.exists().compile().fetchval(connection))

    async def delete_expired(self) -> int:
        async with self._database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                status: CommandComplete[DeleteCommandTag] = await (Query
                    .delete()
                    .from_table(self.table_name)
                    .where()
                    .field("end_time", Equality.LESS, "(NOW() at time zone 'utc') - interval '7 days'", True)
                    .compile()
                    .execute(connection)
                )
                return status.command_tag.rows

    def _map_record_to_model(
        self,
        record: ExternalGiveawayItemRecord
    ) -> ExternalGiveawayItem:
        return ExternalGiveawayItem(
            identifier=record.id,
            created_at=record.created_at,
            start_time=record.start_time,
            end_time=record.end_time,
            source_name=record.source_name,
            item_type=record.item_type,
            url=record.url,
            preview_url=record.preview_url,
            title=record.title
        )

    def _map_model_to_record(
        self,
        model: ExternalGiveawayItem
    ) -> ExternalGiveawayItemRecord:
        return ExternalGiveawayItemRecord(
            id=model.identifier,
            created_at=model.created_at,
            start_time=model.start_time,
            end_time=model.end_time,
            source_name=model.source_name,
            item_type=model.item_type,
            url=model.url,
            preview_url=model.preview_url,
            title=model.title
        )
