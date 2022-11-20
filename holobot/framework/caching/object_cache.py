from collections.abc import Callable
from typing import Any

from holobot.sdk.caching import CacheEntryPolicy, ConcurrentMemoryCache, IObjectCache
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.lifecycle import IStartable
from holobot.sdk.utils.type_utils import UndefinedType

class ObjectCache(IObjectCache, IStartable):
    """In-memory cache meant to be used as a global singleton in the application."""

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
        value_or_factory: Any | Callable[[Any], Any],
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
