class InvalidMessageLengthError(Exception):
    def __init__(self, length: int, lower_bound: int, upper_bound: int, *args) -> None:
        super().__init__(*args)
        self.length = length
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    @property
    def length(self) -> int:
        return self.__length

    @length.setter
    def length(self, value: int) -> None:
        self.__length = value

    @property
    def lower_bound(self) -> int:
        return self.__lower_bound

    @lower_bound.setter
    def lower_bound(self, value: int) -> None:
        self.__lower_bound = value

    @property
    def upper_bound(self) -> int:
        return self.__upper_bound

    @upper_bound.setter
    def upper_bound(self, value: int) -> None:
        self.__upper_bound = value
