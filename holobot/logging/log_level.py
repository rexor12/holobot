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