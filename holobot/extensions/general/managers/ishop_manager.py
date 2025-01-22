from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.general.models.shops import ShopDisplayInfo, TransactionInfo
from holobot.extensions.general.sdk.shops.models import ShopId, ShopItemId

class IShopManager(Protocol):
    def paginate_shop(
        self,
        shop_id: ShopId,
        page_index: int,
        page_size: int = 5
    ) -> Awaitable[ShopDisplayInfo]:
        ...

    def buy_item(
        self,
        user_id: int,
        shop_item_id: ShopItemId,
        count: int = 1
    ) -> Awaitable[TransactionInfo]:
        ...
