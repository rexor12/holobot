from holobot.extensions.general.sdk.shops.models import ShopItemId

class ShopItemNotFoundError(Exception):
    @property
    def shop_item_id(self) -> ShopItemId:
        return self.__shop_item_id

    def __init__(
        self,
        shop_item_id: ShopItemId,
        message: str | None = None
    ) -> None:
        super().__init__(message)
        self.__shop_item_id = shop_item_id
