from enum import IntFlag, unique

@unique
class Equality(IntFlag):
    NONE = 0
    EQUAL = 1 << 0
    LESS = 1 << 1
    GREATER = 1 << 2
    LIKE = 1 << 3
    LIKE_START = 1 << 4
    LIKE_END = 1 << 5
    LESS_OR_EQUAL = LESS | EQUAL
    GREATER_OR_EQUAL = GREATER | EQUAL

    def to_operator(self) -> str:
        if self is Equality.NONE:
            raise ValueError("Unspecified equality.")
        operator = ""
        if Equality.LESS in self:
            operator = "<"
        if Equality.GREATER in self:
            operator = ">"
        if Equality.EQUAL in self:
            return f"{operator}="
        if Equality.LIKE in self or Equality.LIKE_START in self or Equality.LIKE_END in self:
            return "LIKE"
        return operator
