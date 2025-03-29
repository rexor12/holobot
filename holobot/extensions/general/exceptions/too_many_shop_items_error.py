from holobot.extensions.general.sdk.shops.models import ShopId

class TooManyShopItemsError(Exception):
    @property
    def shop_id(self) -> ShopId:
        return self.__shop_id

    @property
    def shop_item_count(self) -> int:
        return self.__shop_item_count

    @property
    def shop_item_count_max(self) -> int:
        return self.__shop_item_count_max

    def __init__(
        self,
        shop_id: ShopId,
        shop_item_count: int,
        shop_item_count_max: int,
        message: str | None = None
    ) -> None:
        super().__init__(message)
        self.__shop_id = shop_id
        self.__shop_item_count = shop_item_count
        self.__shop_item_count_max = shop_item_count_max
