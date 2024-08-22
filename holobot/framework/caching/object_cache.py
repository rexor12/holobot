from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from holobot.sdk.caching import CacheEntryPolicy, CacheView, ConcurrentMemoryCache, IObjectCache
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.lifecycle import IStartable
from holobot.sdk.utils.type_utils import UndefinedType

TKey = TypeVar("TKey")
TValue = TypeVar("TValue")

class ObjectCache(IObjectCache, IStartable):
    """In-memory cache meant to be used as a global singleton in the application."""

    @property
    def priority(self) -> int:
        return 100

    def __init__(self) -> None:
        super().__init__()
        self.__cache: ConcurrentMemoryCache[Any, Any] | None = None

    async def start(self):
        self.__cache = ConcurrentMemoryCache()

    async def stop(self):
        if self.__cache:
            await self.__cache.dispose()

    async def get(self, key: Any) -> Any | UndefinedType:
        if not self.__cache:
            raise InvalidOperationError("The cache hasn't been initialized.")

        return await self.__cache.get(key)

    async def get_or_add(
        self,
        key: Any,
        value_or_factory: Any | Callable[[Any], Awaitable[Any]],
        policy: CacheEntryPolicy | None = None
    ) -> Any | UndefinedType:
        if not self.__cache:
            raise InvalidOperationError("The cache hasn't been initialized.")

        return await self.__cache.get_or_add(key, value_or_factory, policy)

    async def add_or_replace(
        self,
        key: Any,
        value: Any,
        policy: CacheEntryPolicy | None = None
    ) -> Any | UndefinedType:
        if not self.__cache:
            raise InvalidOperationError("The cache hasn't been initialized.")

        return await self.__cache.add_or_replace(key, value, policy)

    def remove(self, key: Any) -> Awaitable[Any | None]:
        if not self.__cache:
            raise InvalidOperationError("The cache hasn't been initialized.")

        return self.__cache.remove(key)

    def get_view(
        self,
        key_type: type[TKey],
        value_type: type[TValue]
    ) -> CacheView[TKey, TValue]:
        return CacheView[key_type, value_type](
            value_type,
            self
        )
