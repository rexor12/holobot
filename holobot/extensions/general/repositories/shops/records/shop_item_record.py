from dataclasses import dataclass

from holobot.extensions.general.enums import ItemType
from holobot.sdk.database.entities import PrimaryKey, Record
from holobot.sdk.database.repositories import manually_generated_key

@manually_generated_key
@dataclass
class ShopItemRecord(Record):
    server_id: PrimaryKey[int]
    shop_id: PrimaryKey[int]
    serial_id: PrimaryKey[int]
    item_type: ItemType
    item_id1: int
    item_id2: int | None
    item_id3: int | None
    count: int
    price_currency_id: int
    price_amount: int
