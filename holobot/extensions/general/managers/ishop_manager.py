from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.general.models.shops import (
    DetailedShopDisplayInfo, ShopDisplayInfo, TransactionInfo
)
from holobot.extensions.general.sdk.shops.models import ShopId, ShopItemId
from holobot.sdk.queries import PaginationResult

class IShopManager(Protocol):
    def paginate_shops(
        self,
        server_id: int,
        name_part: str | None,
        page_index: int,
        page_size: int = 5
    ) -> Awaitable[PaginationResult[ShopDisplayInfo]]:
        ...

    def paginate_shop(
        self,
        shop_id: ShopId,
        page_index: int,
        page_size: int = 5
    ) -> Awaitable[DetailedShopDisplayInfo]:
        ...

    def buy_item(
        self,
        user_id: int,
        shop_item_id: ShopItemId,
        count: int = 1
    ) -> Awaitable[TransactionInfo]:
        ...
