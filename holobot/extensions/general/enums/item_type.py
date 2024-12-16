from enum import IntEnum, unique

@unique
class ItemType(IntEnum):
    INVALID = 0
    CURRENCY = 1
    BADGE = 2
    BACKGROUND = 3
