from .command_tag import CommandTag

class DeleteCommandTag(CommandTag):
    def __init__(self, rows: int, raw_value: str) -> None:
        super().__init__(raw_value)
        self.__rows: int = rows

    @property
    def rows(self) -> int:
        return self.__rows
    
    def __repr__(self) -> str:
        return "DeleteCommandTag(%s)" % self.__rows
