from collections.abc import Awaitable, Callable
from typing import Generic, TypeVar, cast

T = TypeVar("T")

class AsyncLazy(Generic[T]):
    async def get_value(self) -> T:
        if self.__is_value_created:
            return cast(T, self.__value)
        self.__is_value_created = True
        self.__value = await self.__factory()
        return self.__value

    @property
    def is_value_created(self) -> bool:
        return self.__is_value_created

    def __init__(
        self,
        factory: Callable[[], Awaitable[T]]
    ) -> None:
        super().__init__()
        self.__factory = factory
        self.__is_value_created = False
        self.__value: T | None = None
