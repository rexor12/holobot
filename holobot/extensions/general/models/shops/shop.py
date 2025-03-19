from dataclasses import dataclass

from holobot.extensions.general.sdk.shops.models import ShopId
from holobot.sdk.database.entities import AggregateRoot

@dataclass(kw_only=True)
class Shop(AggregateRoot[ShopId]):
    shop_name: str
