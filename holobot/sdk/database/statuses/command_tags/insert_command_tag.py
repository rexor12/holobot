from .command_tag import CommandTag

class InsertCommandTag(CommandTag):
    def __init__(self, oid: str, rows: int, raw_value: str) -> None:
        super().__init__(raw_value)
        self.__oid: str = oid
        self.__rows: int = rows

    @property
    def oid(self) -> str:
        return self.__oid

    @property
    def rows(self) -> int:
        return self.__rows
    
    def __repr__(self) -> str:
        return "InsertCommandTag(%s, %s)" % (self.__oid, self.__rows)
