from threading import Lock
from typing import Awaitable, Callable, Dict, Generic, TypeVar

TKey = TypeVar("TKey")
TValue = TypeVar("TValue")

class ConcurrentCache(Generic[TKey, TValue]):
    def __init__(self):
        self.__dict: Dict[TKey, TValue] = {}
        self.__lock: Lock = Lock()

    async def get_or_add(self, key: TKey, factory: Callable[[TKey], Awaitable[TValue]]) -> TValue:
        if (value := self.__dict.get(key, None)) is not None:
            return value
        self.__lock.acquire()
        if (value := self.__dict.get(key, None)) is not None:
            return value
        try:
            value = await factory(key)
            self.__dict[key] = value
            return value
        finally:
            self.__lock.release()

    async def add_or_update(self, key: TKey,
        add_factory: Callable[[TKey], Awaitable[TValue]],
        update_factory: Callable[[TKey, TValue], Awaitable[TValue]]) -> TValue:
        self.__lock.acquire()
        try:
            if (value := self.__dict.get(key, None)) is not None:
                value = await update_factory(key, value)
                self.__dict[key] = value
                return value
            value = await add_factory(key)
            self.__dict[key] = value
            return value
        finally:
            self.__lock.release()