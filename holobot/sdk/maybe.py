from typing import Generic, Optional, TypeVar

T = TypeVar("T")

class Maybe(Generic[T]):
    def __init__(self, value: Optional[T] = None) -> None:
        super().__init__()
        self.__value: Optional[T] = value
    
    @property
    def value(self) -> T:
        if self.__value is None:
            raise ValueError("There is no value.")
        return self.__value

    @property
    def has_value(self) -> bool:
        return self.__value is not None

    def __repr__(self) -> str:
        return f"<Maybe has_value={self.has_value}, value={self.__value}>"

    def __bool__(self) -> bool:
        return self.__value is not None
