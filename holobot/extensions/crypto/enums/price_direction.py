from enum import IntEnum, unique

@unique
class PriceDirection(IntEnum):
    ABOVE = 0
    BELOW = 1

    def __str__(self) -> str:
        return "below" if self is PriceDirection.BELOW else "above"

    @staticmethod
    def parse(value: str):
        match value.upper():
            case "ABOVE": return PriceDirection.ABOVE
            case "BELOW": return PriceDirection.BELOW
            case _: return None
