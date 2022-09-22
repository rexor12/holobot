from enum import IntEnum, unique

@unique
class FrequencyType(IntEnum):
    DAYS = 0
    HOURS = 1
    MINUTES = 2

    def __str__(self) -> str:
        match self:
            case FrequencyType.HOURS: return "hours"
            case FrequencyType.MINUTES: return "minutes"
            case _: return "days"

    @staticmethod
    def parse(value: str):
        match value.upper():
            case "DAYS": return FrequencyType.DAYS
            case "HOURS": return FrequencyType.HOURS
            case "MINUTES": return FrequencyType.MINUTES
            case _: return None
