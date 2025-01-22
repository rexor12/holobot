from holobot.extensions.general.enums import ItemType
from holobot.extensions.general.sdk.shops.models import ShopItemId

class UnknownShopItemTypeError(Exception):
    @property
    def shop_item_id(self) -> ShopItemId:
        return self.__shop_item_id

    @property
    def item_type(self) -> ItemType:
        return self.__item_type

    def __init__(
        self,
        shop_item_id: ShopItemId,
        item_type: ItemType,
        message: str | None = None
    ) -> None:
        super().__init__(message)
        self.__shop_item_id = shop_item_id
        self.__item_type = item_type
