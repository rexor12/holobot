from enum import IntEnum, unique

@unique
class ReminderLocation(IntEnum):
    DIRECT_MESSAGE = 0
    CHANNEL = 1
