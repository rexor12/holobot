from enum import IntEnum, unique

@unique
class OptionType(IntEnum):
    STRING = 0
    BOOLEAN = 1
    INTEGER = 2
    FLOAT = 3
