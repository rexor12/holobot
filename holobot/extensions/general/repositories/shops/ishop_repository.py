from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.general.models.shops import Shop, ShopDisplayInfo
from holobot.extensions.general.sdk.shops.models import ShopId
from holobot.sdk.database.repositories import IRepository
from holobot.sdk.queries import PaginationResult

class IShopRepository(IRepository[ShopId, Shop], Protocol):
    def exists(
        self,
        shop_id: ShopId
    ) -> Awaitable[bool]:
        ...

    def paginate_shop_infos(
        self,
        server_id: int,
        name_part: str | None,
        page_index: int,
        page_size: int
    ) -> Awaitable[PaginationResult[ShopDisplayInfo]]:
        ...

    def count_by_server(
        self,
        server_id: int
    ) -> Awaitable[int]:
        ...

    def get_shop_name(
        self,
        shop_id: ShopId
    ) -> Awaitable[str | None]:
        ...
