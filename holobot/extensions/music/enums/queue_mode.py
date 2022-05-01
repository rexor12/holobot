from enum import IntEnum, unique

@unique
class QueueMode(IntEnum):
    AS_LAST = 0
    AS_FIRST = 1
    SKIP_CURRENT = 2
    
    @staticmethod
    def parse(value: int) -> 'QueueMode':
        try:
            return QueueMode(value)
        except (ValueError):
            return QueueMode.AS_LAST
