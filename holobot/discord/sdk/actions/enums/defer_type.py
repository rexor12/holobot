from enum import IntEnum, unique

@unique
class DeferType(IntEnum):
    NONE = 0
    DEFER_MESSAGE_CREATION = 1
    DEFER_MESSAGE_UPDATE = 2
