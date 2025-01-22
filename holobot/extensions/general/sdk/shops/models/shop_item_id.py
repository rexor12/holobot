from dataclasses import dataclass

from holobot.sdk.database.entities import Identifier

@dataclass(kw_only=True)
class ShopItemId(Identifier):
    server_id: int
    """The identifier of the server the shop belongs to.

    Should be set to "0" if it's a global shop.
    """

    shop_id: int
    """The server-local identifier of the shop."""

    serial_id: int
    """The server-local identifier of the item."""

    def __str__(self) -> str:
        return f"ShopItem/{self.server_id}/{self.shop_id}/{self.serial_id}"

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, ShopItemId):
            return False

        return (
            self.server_id == value.server_id
            and self.shop_id == value.shop_id
            and self.serial_id == value.serial_id
        )

    @staticmethod
    def create(server_id: int, shop_id: int, serial_id: int) -> 'ShopItemId':
        return ShopItemId(
            server_id=server_id,
            shop_id=shop_id,
            serial_id=serial_id
        )
