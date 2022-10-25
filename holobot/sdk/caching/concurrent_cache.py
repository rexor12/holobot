from asyncio.locks import Lock
from collections.abc import Awaitable, Callable
from typing import Any, Generic, TypeVar

from holobot.sdk.exceptions import ArgumentError
from holobot.sdk.utils import UNDEFINED, UndefinedType

TKey = TypeVar("TKey")
TValue = TypeVar("TValue")
TParam = TypeVar("TParam")
TParam2 = TypeVar("TParam2")

class ConcurrentCache(Generic[TKey, TValue]):
    def __init__(self):
        self.__dict: dict[TKey, TValue] = {}
        self.__lock: Lock = Lock()

    async def get(self, key: TKey) -> TValue | UndefinedType:
        async with self.__lock:
            return self.__dict.get(key, UNDEFINED)

    async def get_or_add(
        self,
        key: TKey,
        factory: Callable[[TKey], Awaitable[TValue]]
    ) -> TValue:
        return await self.__get_or_add(key, factory)

    async def get_or_add2(
        self,
        key: TKey,
        factory: Callable[[TKey, TParam], Awaitable[TValue]],
        param: TParam
    ) -> TValue:
        return await self.__get_or_add(key, factory, param)

    async def get_or_add3(
        self,
        key: TKey,
        factory: Callable[[TKey], TValue]
    ) -> TValue:
        return await self.__get_or_add2(key, factory)

    async def add(
        self,
        key: TKey,
        add_factory: Callable[[TKey], Awaitable[TValue]]
    ) -> TValue:
        return await self.__add(key, add_factory)

    async def add2(
        self,
        key: TKey,
        add_factory: Callable[[TKey, TParam], Awaitable[TValue]],
        param: TParam
    ) -> TValue:
        return await self.__add(key, add_factory, param)

    async def add3(
        self,
        key: TKey,
        add_factory: Callable[[TKey, TParam, TParam2], Awaitable[TValue]],
        param1: TParam,
        param2: TParam2
    ) -> TValue:
        return await self.__add(key, add_factory, param1, param2)

    async def add_or_update(
        self,
        key: TKey,
        add_factory: Callable[[TKey], Awaitable[TValue]],
        update_factory: Callable[[TKey, TValue], Awaitable[TValue]]
    ) -> tuple[TValue | UndefinedType, TValue]:
        async with self.__lock:
            if (old_value := self.__dict.get(key, UNDEFINED)) is UNDEFINED:
                new_value = await add_factory(key)
            else:
                new_value = await update_factory(key, old_value)

            self.__dict[key] = new_value
            return (old_value, new_value)

    async def add_or_update2(
        self,
        key: TKey,
        add_factory: Callable[[TKey], TValue],
        update_factory: Callable[[TKey, TValue], TValue]
    ) -> tuple[TValue | UndefinedType, TValue]:
        async with self.__lock:
            if (old_value := self.__dict.get(key, UNDEFINED)) is UNDEFINED:
                new_value = add_factory(key)
            else:
                new_value = update_factory(key, old_value)

            self.__dict[key] = new_value
            return (old_value, new_value)

    async def add_or_update3(
        self,
        key: TKey,
        add_factory: Callable[[TKey, TParam], TValue],
        update_factory: Callable[[TKey, TValue, TParam], TValue],
        param: TParam
    ) -> tuple[TValue | UndefinedType, TValue]:
        async with self.__lock:
            if (old_value := self.__dict.get(key, UNDEFINED)) is UNDEFINED:
                new_value = add_factory(key, param)
            else:
                new_value = update_factory(key, old_value, param)

            self.__dict[key] = new_value
            return (old_value, new_value)

    async def remove(self, key: TKey) -> TValue:
        async with self.__lock:
            if (value := self.__dict.pop(key, UNDEFINED)) is UNDEFINED:
                raise ArgumentError("key", "The specified key is not present.")
            return value

    async def __get_or_add(self, key: TKey, factory: Callable[..., Awaitable[TValue]], *args: Any) -> TValue:
        async with self.__lock:
            if (value := self.__dict.get(key, UNDEFINED)) is not UNDEFINED:
                return value

            value = await factory(key, *args)
            self.__dict[key] = value
            return value

    async def __get_or_add2(self, key: TKey, factory: Callable[..., TValue], *args: Any) -> TValue:
        async with self.__lock:
            if (value := self.__dict.get(key, UNDEFINED)) is not UNDEFINED:
                return value

            value = factory(key, *args)
            self.__dict[key] = value
            return value

    async def __add(self, key: TKey, add_factory: Callable[..., Awaitable[TValue]], *args: Any) -> TValue:
        async with self.__lock:
            if key in self.__dict:
                raise ArgumentError("key", "An item with the specified key is already present.")

            value = await add_factory(key, *args)
            self.__dict[key] = value
            return value
