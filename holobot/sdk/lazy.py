from typing import Callable, Generic, TypeVar, cast

T = TypeVar("T")

class Lazy(Generic[T]):
    @property
    def value(self) -> T:
        if self.__is_value_created:
            return cast(T, self.__value)
        self.__is_value_created = True
        self.__value = self.__factory()
        return self.__value

    @property
    def is_value_created(self) -> bool:
        return self.__is_value_created

    def __init__(
        self,
        factory: Callable[[], T]
    ) -> None:
        super().__init__()
        self.__factory = factory
        self.__is_value_created = False
        self.__value: T | None = None
