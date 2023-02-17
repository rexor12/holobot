from enum import IntEnum, unique

@unique
class ReactionType(IntEnum):
    UNKNOWN = 0
    HUG = 1
    KISS = 2
    PAT = 3
    POKE = 4
