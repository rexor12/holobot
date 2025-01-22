from typing import Protocol

from holobot.extensions.general.models.shops import Shop
from holobot.extensions.general.sdk.shops.models import ShopId
from holobot.sdk.database.repositories import IRepository

class IShopRepository(IRepository[ShopId, Shop], Protocol):
    ...
