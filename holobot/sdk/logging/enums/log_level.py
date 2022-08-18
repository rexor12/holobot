from enum import IntEnum, unique

@unique
class LogLevel(IntEnum):
    TRACE = 0
    DEBUG = 1
    INFORMATION = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5
    NONE = 6

    @staticmethod
    def parse(value: str):
        return LogLevel.__members__.get(value.upper(), LogLevel.WARNING)
