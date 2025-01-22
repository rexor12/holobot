from collections.abc import Awaitable

from holobot.extensions.general.models.shops import ShopItem
from holobot.extensions.general.repositories.shops.records import ShopItemRecord
from holobot.extensions.general.sdk.shops.models import ShopId, ShopItemId
from holobot.sdk.database import IDatabaseManager, IUnitOfWorkProvider
from holobot.sdk.database.entities import PrimaryKey
from holobot.sdk.database.queries.enums import Connector, Equality, Order
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.queries import PaginationResult
from .ishop_item_repository import IShopItemRepository

@injectable(IShopItemRepository)
class ShopItemRepository(
    RepositoryBase[ShopItemId, ShopItemRecord, ShopItem],
    IShopItemRepository
):
    @property
    def record_type(self) -> type[ShopItemRecord]:
        return ShopItemRecord

    @property
    def model_type(self) -> type[ShopItem]:
        return ShopItem

    @property
    def identifier_type(self) -> type[ShopItemId]:
        return ShopItemId

    @property
    def table_name(self) -> str:
        return "shop_items"

    def __init__(
        self,
        database_manager: IDatabaseManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__(database_manager, unit_of_work_provider)

    def paginate(
        self,
        shop_id: ShopId,
        page_index: int,
        page_size: int
    ) -> Awaitable[PaginationResult[ShopItem]]:
        return self._paginate(
            (("serial_id", Order.ASCENDING),),
            page_index,
            page_size,
            lambda where: where.fields(
                Connector.AND,
                ("server_id", Equality.EQUAL, shop_id.server_id),
                ("shop_id", Equality.EQUAL, shop_id.shop_id)
            )
        )

    def _map_record_to_model(self, record: ShopItemRecord) -> ShopItem:
        return ShopItem(
            identifier=ShopItemId(
                server_id=record.server_id.value,
                shop_id=record.shop_id.value,
                serial_id=record.serial_id.value
            ),
            item_type=record.item_type,
            item_id1=record.item_id1,
            item_id2=record.item_id2,
            item_id3=record.item_id3,
            count=record.count,
            price_currency_id=record.price_currency_id,
            price_amount=record.price_amount
        )

    def _map_model_to_record(self, model: ShopItem) -> ShopItemRecord:
        return ShopItemRecord(
            server_id=PrimaryKey(model.identifier.server_id),
            shop_id=PrimaryKey(model.identifier.shop_id),
            serial_id=PrimaryKey(model.identifier.serial_id),
            item_type=model.item_type,
            item_id1=model.item_id1,
            item_id2=model.item_id2,
            item_id3=model.item_id3,
            count=model.count,
            price_currency_id=model.price_currency_id,
            price_amount=model.price_amount
        )
