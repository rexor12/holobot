from enum import IntEnum, unique

@unique
class ComponentStyle(IntEnum):
    PRIMARY = 0
    SECONDARY = 1
    SUCCESS = 2
    DANGER = 3
    LINK = 4
