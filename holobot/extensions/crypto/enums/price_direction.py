from enum import IntEnum, unique

@unique
class PriceDirection(IntEnum):
    ABOVE = 0
    BELOW = 1

    def __str__(self) -> str:
        if self is PriceDirection.BELOW:
            return "below"
        return "above"

    @staticmethod
    def parse(value: str):
        value = value.upper()
        if value == "ABOVE":
            return PriceDirection.ABOVE
        if value == "BELOW":
            return PriceDirection.BELOW
        return None
