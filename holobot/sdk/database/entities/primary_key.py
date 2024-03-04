from typing import Generic, TypeVar

T = TypeVar("T")

class PrimaryKey(Generic[T]):
    @property
    def value(self) -> T:
        return self.__value

    @value.setter
    def value(self, value: T) -> None:
        self.__value = value

    def __init__(self, value: T) -> None:
        super().__init__()
        self.value = value
