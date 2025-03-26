from collections.abc import Awaitable

from holobot.extensions.general.models.shops import Shop, ShopDisplayInfo
from holobot.extensions.general.repositories.shops.records import ShopRecord
from holobot.extensions.general.sdk.shops.models import ShopId
from holobot.sdk.database import IDatabaseManager, IUnitOfWorkProvider
from holobot.sdk.database.entities import PrimaryKey
from holobot.sdk.database.queries import Query
from holobot.sdk.database.queries.enums import Connector, Equality, Order
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.queries import PaginationResult
from .ishop_repository import IShopRepository
from .records import ShopRecord

@injectable(IShopRepository)
class ShopRepository(
    RepositoryBase[ShopId, ShopRecord, Shop],
    IShopRepository
):
    @property
    def record_type(self) -> type[ShopRecord]:
        return ShopRecord

    @property
    def model_type(self) -> type[Shop]:
        return Shop

    @property
    def identifier_type(self) -> type[ShopId]:
        return ShopId

    @property
    def table_name(self) -> str:
        return "shops"

    def __init__(
        self,
        database_manager: IDatabaseManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__(database_manager, unit_of_work_provider)

    def exists(
        self,
        shop_id: ShopId
    ) -> Awaitable[bool]:
        return self._exists_by_filter(
            lambda where: where.fields(
                Connector.AND,
                ("server_id", Equality.EQUAL, shop_id.server_id),
                ("shop_id", Equality.EQUAL, shop_id.shop_id)
            )
        )

    async def paginate_shop_infos(
        self,
        server_id: int,
        name_part: str | None,
        page_index: int,
        page_size: int
    ) -> PaginationResult[ShopDisplayInfo]:
        async with (session := await self._get_session()):
            query = (Query
                .select()
                .columns("shop_id", "shop_name")
                .from_table(self.table_name, schema_name=self.schema_name)
                .where()
                .field("server_id", Equality.EQUAL, server_id)
            )

            if name_part:
                query = query.and_field("shop_name", Equality.LIKE, name_part)

            result = await query.paginate(
                (("shop_id", Order.ASCENDING),),
                page_index,
                page_size
            ).compile().fetch(session.connection)

            return PaginationResult[ShopDisplayInfo](
                result.page_index,
                result.page_size,
                result.total_count,
                [
                    ShopDisplayInfo(
                        identifier=record["shop_id"],
                        name=record["shop_name"]
                    )
                    for record in result.records
                ]
            )

    def count_by_server(
        self,
        server_id: int
    ) -> Awaitable[int]:
        return self._count_by_filter(
            lambda where: where.field("server_id", Equality.EQUAL, server_id)
        )

    async def get_shop_name(
        self,
        shop_id: ShopId
    ) -> str | None:
        async with (session := await self._get_session()):
            query = (Query
                .select().column("shop_name")
                .from_table(self.table_name, schema_name=self.schema_name)
                .where()
                .fields(
                    Connector.AND,
                    ("server_id", Equality.EQUAL, shop_id.server_id),
                    ("shop_id", Equality.EQUAL, shop_id.shop_id)
                )
                .limit().max_count(1)
            )

            return await query.compile().fetchval(session.connection)

    def _map_record_to_model(self, record: ShopRecord) -> Shop:
        return Shop(
            identifier=ShopId(
                server_id=record.server_id.value,
                shop_id=record.shop_id.value
            ),
            shop_name=record.shop_name
        )

    def _map_model_to_record(self, model: Shop) -> ShopRecord:
        return ShopRecord(
            server_id=PrimaryKey(model.identifier.server_id),
            shop_id=PrimaryKey(model.identifier.shop_id),
            shop_name=model.shop_name
        )
