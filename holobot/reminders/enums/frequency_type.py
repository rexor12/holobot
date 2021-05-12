from enum import IntEnum, unique

@unique
class FrequencyType(IntEnum):
    NEVER = 0,
    HOURLY = 1,
    DAILY = 2,
    WEEKLY = 3,
    SPECIFIC = 4

    def __str__(self) -> str:
        if self == FrequencyType.SPECIFIC:
            return "specific"
        if self == FrequencyType.WEEKLY:
            return "weekly"
        if self == FrequencyType.DAILY:
            return "daily"
        if self == FrequencyType.HOURLY:
            return "hourly"
        return "not repeating"
    
    # @staticmethod
    # def parse(value: str):
    #     value = value.upper()
    #     if value == "SPECIFIC":
    #         return FrequencyType.SPECIFIC
    #     if value == "WEEKLY":
    #         return FrequencyType.WEEKLY
        
    #     return None