from enum import IntFlag, unique

@unique
class Equality(IntFlag):
    NONE = 0,
    EQUAL = 1 << 0,
    LESS = 1 << 1,
    GREATER = 1 << 2

    def to_operator(self) -> str:
        if self == Equality.NONE:
            raise ValueError("Unspecified equality.")
        operator = ""
        if Equality.LESS in self:
            operator = "<"
        if Equality.GREATER in self:
            operator = ">"
        if Equality.EQUAL in self:
            return f"{operator}="
        return operator
