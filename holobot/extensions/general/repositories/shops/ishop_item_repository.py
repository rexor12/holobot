from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.general.models.shops import ShopItem
from holobot.extensions.general.sdk.shops.models import ShopId, ShopItemId
from holobot.sdk.database.repositories import IRepository
from holobot.sdk.queries import PaginationResult

class IShopItemRepository(IRepository[ShopItemId, ShopItem], Protocol):
    def paginate(
        self,
        shop_id: ShopId,
        page_index: int,
        page_size: int
    ) -> Awaitable[PaginationResult[ShopItem]]:
        ...

    def count_by_shop(
        self,
        shop_id: ShopId
    ) -> Awaitable[int]:
        ...
