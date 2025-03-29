from holobot.extensions.general.sdk.shops.models import ShopId

class ShopNotAvailableError(Exception):
    @property
    def shop_id(self) -> ShopId:
        return self.__shop_id

    def __init__(
        self,
        shop_id: ShopId,
        message: str | None = None
    ) -> None:
        super().__init__(message)
        self.__shop_id = shop_id
