from holobot.extensions.general.models.shops import Shop
from holobot.extensions.general.repositories.shops.records import ShopRecord
from holobot.extensions.general.sdk.shops.models import ShopId
from holobot.sdk.database import IDatabaseManager, IUnitOfWorkProvider
from holobot.sdk.database.entities import PrimaryKey
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.ioc.decorators import injectable
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
