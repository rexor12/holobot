from enum import IntEnum, unique

@unique
class ReactionType(IntEnum):
    UNKNOWN = 0
    HUG = 1
    KISS = 2
    PAT = 3
    POKE = 4
    LICK = 5
    BITE = 6
    HANDHOLD = 7
    CUDDLE = 8
