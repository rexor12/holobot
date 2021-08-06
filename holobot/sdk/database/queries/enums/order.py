from enum import IntEnum, unique

@unique
class Order(IntEnum):
    ASCENDING = 0,
    DESCENDING = 1
