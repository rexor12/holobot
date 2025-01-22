from dataclasses import dataclass

from holobot.sdk.database.entities import Identifier

@dataclass(kw_only=True)
class ShopId(Identifier):
    server_id: int
    """The identifier of the server the shop belongs to.

    Should be set to "0" if it's a global shop.
    """

    shop_id: int
    """The server-local identifier of the shop."""

    def __str__(self) -> str:
        return f"Shop/{self.server_id}/{self.shop_id}"

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, ShopId):
            return False

        return (
            self.server_id == value.server_id
            and self.shop_id == value.shop_id
        )

    @staticmethod
    def create(server_id: int, shop_id: int) -> 'ShopId':
        return ShopId(
            server_id=server_id,
            shop_id=shop_id
        )
