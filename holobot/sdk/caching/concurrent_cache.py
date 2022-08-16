from asyncio.locks import Lock
from holobot.sdk.exceptions import ArgumentError
from typing import Any, Awaitable, Callable, Generic, TypeVar

TKey = TypeVar("TKey")
TValue = TypeVar("TValue")
TParam = TypeVar("TParam")
TParam2 = TypeVar("TParam2")

class ConcurrentCache(Generic[TKey, TValue]):
    def __init__(self):
        self.__dict: dict[TKey, TValue] = {}
        self.__lock: Lock = Lock()

    async def get(self, key: TKey) -> TValue | None:
        return self.__dict.get(key, None)

    async def get_or_add(self, key: TKey, factory: Callable[[TKey], Awaitable[TValue]]) -> TValue:
        return await self.__get_or_add(key, factory)

    async def get_or_add2(self, key: TKey, factory: Callable[[TKey, TParam], Awaitable[TValue]], param: TParam) -> TValue:
        return await self.__get_or_add(key, factory, param)

    async def add(self, key: TKey, add_factory: Callable[[TKey], Awaitable[TValue]]) -> TValue:
        return await self.__add(key, add_factory)

    async def add2(self, key: TKey, add_factory: Callable[[TKey, TParam], Awaitable[TValue]], param: TParam) -> TValue:
        return await self.__add(key, add_factory, param)

    async def add3(self, key: TKey, add_factory: Callable[[TKey, TParam, TParam2], Awaitable[TValue]], param1: TParam, param2: TParam2) -> TValue:
        return await self.__add(key, add_factory, param1, param2)

    async def add_or_update(self, key: TKey,
        add_factory: Callable[[TKey], Awaitable[TValue]],
        update_factory: Callable[[TKey, TValue], Awaitable[TValue]]) -> TValue:
        async with self.__lock:
            if (value := self.__dict.get(key, None)) is not None:
                value = await update_factory(key, value)
                self.__dict[key] = value
                return value

            value = await add_factory(key)
            self.__dict[key] = value
            return value

    async def remove(self, key: TKey) -> TValue:
        async with self.__lock:
            if (value := self.__dict.pop(key, None)) is None:
                raise ArgumentError("key", "The specified key is not present.")
            return value

    async def __get_or_add(self, key: TKey, factory: Callable[..., Awaitable[TValue]], *args: Any) -> TValue:
        if (value := self.__dict.get(key, None)) is not None:
            return value

        async with self.__lock:
            if (value := self.__dict.get(key, None)) is not None:
                return value

            value = await factory(key, *args)
            self.__dict[key] = value
            return value

    async def __add(self, key: TKey, add_factory: Callable[..., Awaitable[TValue]], *args: Any) -> TValue:
        async with self.__lock:
            if (value := self.__dict.get(key, None)) is not None:
                raise ArgumentError("key", "An item with the specified key is already present.")

            value = await add_factory(key, *args)
            self.__dict[key] = value
            return value
