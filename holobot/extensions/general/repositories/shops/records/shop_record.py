from dataclasses import dataclass

from holobot.sdk.database.entities import PrimaryKey, Record
from holobot.sdk.database.repositories import manually_generated_key

@manually_generated_key
@dataclass
class ShopRecord(Record):
    server_id: PrimaryKey[int]
    shop_id: PrimaryKey[int]
    shop_name: str
