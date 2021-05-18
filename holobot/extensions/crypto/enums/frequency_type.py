from enum import IntEnum, unique

@unique
class FrequencyType(IntEnum):
    DAYS = 0
    HOURS = 1
    MINUTES = 2

    def __str__(self) -> str:
        if self == FrequencyType.HOURS:
            return "hours"
        if self == FrequencyType.MINUTES:
            return "minutes"
        return "days"
    
    @staticmethod
    def parse(value: str):
        value = value.upper()
        if value == "DAYS":
            return FrequencyType.DAYS
        if value == "HOURS":
            return FrequencyType.HOURS
        if value == "MINUTES":
            return FrequencyType.MINUTES
        return None
