class CommandTag:
    def __init__(self, raw_value: str) -> None:
        self.__raw_value: str = raw_value

    @property
    def raw_value(self) -> str:
        return self.__raw_value
