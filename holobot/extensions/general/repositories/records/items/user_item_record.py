from dataclasses import dataclass

from holobot.extensions.general.enums import ItemType
from holobot.sdk.database.entities import PrimaryKey, Record
from holobot.sdk.database.repositories import manually_generated_key

@manually_generated_key
@dataclass(kw_only=True)
class UserItemRecord(Record):
    user_id: PrimaryKey[int]
    server_id: PrimaryKey[int]
    serial_id: PrimaryKey[int]
    item_type: ItemType
    item_id1: int | None
    item_id2: int | None
    item_id3: int | None
    count: int
    item_data_json: str
