from dataclasses import dataclass, field

from .shop_item_display_info import ShopItemDisplayInfo

@dataclass(kw_only=True)
class DetailedShopDisplayInfo:
    name: str
    page_index: int
    page_size: int
    item_count: int
    items: list[ShopItemDisplayInfo] = field(default_factory=list)
