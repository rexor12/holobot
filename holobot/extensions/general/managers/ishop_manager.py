from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.general.models.items import BadgeDisplayInfo, CurrencyDisplayInfo
from holobot.extensions.general.models.shops import (
    DetailedShopDisplayInfo, ShopDisplayInfo, TransactionInfo
)
from holobot.extensions.general.sdk.badges.models import BadgeId
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

    def create_shop(
        self,
        server_id: int,
        shop_name: str
    ) -> Awaitable[ShopId]:
        ...

    def get_shop_name(
        self,
        shop_id: ShopId
    ) -> Awaitable[str | None]:
        ...

    def remove_shop(
        self,
        shop_id: ShopId
    ) -> Awaitable[int]:
        ...

    def remove_shop_item(
        self,
        shop_item_id: ShopItemId
    ) -> Awaitable[int]:
        ...

    def add_badge_to_shop(
        self,
        shop_id: ShopId,
        badge_id: BadgeId,
        currency_id: int,
        currency_amount: int
    ) -> Awaitable[tuple[BadgeDisplayInfo, CurrencyDisplayInfo]]:
        ...

    def add_currency_to_shop(
        self,
        shop_id: ShopId,
        currency_id: int,
        currency_amount: int,
        price_currency_id: int,
        price_currency_amount: int
    ) -> Awaitable[tuple[CurrencyDisplayInfo, CurrencyDisplayInfo]]:
        ...
