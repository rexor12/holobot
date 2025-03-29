from dataclasses import dataclass

from holobot.extensions.general.models.items import ItemDisplayInfoBase
from holobot.extensions.general.sdk.shops.models import ShopItemId

@dataclass(kw_only=True)
class ShopItemDisplayInfo:
    item_id: ShopItemId
    count: int
    currency_emoji_name: str
    currency_emoji_id: int
    price: int
    item_info: ItemDisplayInfoBase
