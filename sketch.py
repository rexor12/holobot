from dataclasses import dataclass
from enum import IntEnum, unique

from holobot.extensions.general.sdk.badges.models import BadgeId
from holobot.sdk.serialization import json_type_hierarchy_root
from holobot.sdk.serialization.json_serializer import JsonSerializer

@unique
class ItemType(IntEnum):
    INVALID = 0
    CURRENCY = 1
    BADGE = 2
    BACKGROUND = 3

# class AbstractDataclass(ABC):
#     def __new__(cls) :
#         if cls == AbstractDataclass or cls.__bases__[0] == AbstractDataclass:
#             raise TypeError("Cannot instantiate abstract class.")
#         return super().__new__(cls)

#region Storage

@json_type_hierarchy_root()
@dataclass(kw_only=True)
class ItemStorageModelBase:
    count: int

@dataclass(kw_only=True)
class CurrencyItemStorageModel(ItemStorageModelBase):
    currency_id: int

@dataclass(kw_only=True)
class BadgeItemStorageModel(ItemStorageModelBase):
    server_id: int
    badge_id: int

@dataclass(kw_only=True)
class BackgroundItemStorageModel(ItemStorageModelBase):
    background_id: int

@dataclass(kw_only=True)
class UserItemRecord:
    user_id: int
    serial_id: int
    server_id: int
    item_type: ItemType
    item_id1: int | None
    item_id2: int | None
    item_id3: int | None
    item_data_json: str

serializer = JsonSerializer({
    CurrencyItemStorageModel,
    BadgeItemStorageModel,
    BackgroundItemStorageModel
})

#endregion

#region Domain

@dataclass
class ItemBase:
    count: int

@dataclass
class CurrencyItem(ItemBase):
    currency_id: int

@dataclass
class BadgeItem(ItemBase):
    badge_id: BadgeId

@dataclass
class BackgroundItem(ItemBase):
    background_id: int

@dataclass
class UserItem:
    user_id: int
    """The identifier of the owning user."""

    server_id: int

    serial_id: int
    """An identifier unique in context of the user and the server.

    Multiple user items belonging to different users may have the same serial IDs.
    """


    # Helpers for database queries. The concrete meaning is determined by the item type.
    item_id1: int | None
    item_id2: int | None
    item_id3: int | None

    item: ItemBase
    """The details of the item."""

#endregion

# @dataclass
# class UserInventory:
#     user_id: str

record = UserItemRecord(
    user_id=123,
    server_id=1,
    serial_id=1,
    item_type=ItemType.BADGE,
    item_id1=0, # server_id
    item_id2=1, # badge_id
    item_id3=None,
    item_data_json=serializer.serialize(
        BadgeItemStorageModel(
            count=1,
            server_id=0,
            badge_id=1
        )
    )
)

print(f"serialized: {record.item_data_json}")
item_data = serializer.deserialize2(record.item_data_json)
print(item_data)

item = UserItem(
    1,
    0,
    1,
    1,
    None,
    None,
    BadgeItem(
        1,
        BadgeId(server_id=123456, badge_id=1)
    )
)
