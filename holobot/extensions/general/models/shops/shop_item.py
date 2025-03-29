from dataclasses import dataclass

from holobot.extensions.general.enums import ItemType
from holobot.extensions.general.sdk.shops.models import ShopItemId
from holobot.sdk.database.entities import AggregateRoot

@dataclass(kw_only=True)
class ShopItem(AggregateRoot[ShopItemId]):
    item_type: ItemType
    item_id1: int
    item_id2: int | None
    item_id3: int | None
    count: int
    price_currency_id: int
    price_amount: int
