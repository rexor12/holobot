from dataclasses import dataclass, field

from holobot.extensions.general.models.items import ItemDisplayInfoBase

@dataclass(kw_only=True)
class ShopDisplayInfo:
    name: str
    page_index: int
    page_size: int
    item_count: int
    items: list[ItemDisplayInfoBase] = field(default_factory=list)
