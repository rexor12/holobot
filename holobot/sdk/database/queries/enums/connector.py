from enum import IntEnum, unique

@unique
class Connector(IntEnum):
    AND = 0
    OR = 1
