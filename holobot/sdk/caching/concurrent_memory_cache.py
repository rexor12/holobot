import asyncio
import os
from collections.abc import Awaitable, Callable
from datetime import timedelta
from typing import Any, Generic, TypeVar, cast

from holobot.sdk import IDisposable
from holobot.sdk.concurrency import IAsyncDisposable
from holobot.sdk.exceptions import ArgumentError
from holobot.sdk.logging import ILogger, ILoggerFactory
from holobot.sdk.threading import CancellationToken, CancellationTokenSource
from holobot.sdk.threading.utils import wait
from holobot.sdk.utils import UNDEFINED, UndefinedType
from holobot.sdk.utils.timedelta_utils import ZERO_TIMEDELTA
from .cache_entry_policy import CacheEntryPolicy
from .icache import ICache
from .no_expiration_cache_entry_policy import NoExpirationCacheEntryPolicy

TKey = TypeVar("TKey")
TValue = TypeVar("TValue")

# On most Linux systems, sched_getaffinity returns the processor cores
# available to the executing Python process. When unavailable, we fall back to 4.
DEGREE_OF_PARALLELISM = (
    len(os.sched_getaffinity(0)) # type: ignore
    if hasattr(os, "sched_getaffinity")
    else 4
)

DEFAULT_CLEANUP_INTERVAL = timedelta(seconds=20)

class _CacheEntryKey(Generic[TKey]):
    @property
    def key(self) -> TKey:
        return self.__key

    @property
    def hash_value(self) -> int:
        return self.__hash

    def __init__(self, key: TKey) -> None:
        super().__init__()
        self.__key = key
        self.__hash = hash(key)

    def __hash__(self) -> int:
        return self.__hash

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, _CacheEntryKey) and __o.key == self.key

class _CacheEntry(Generic[TValue]):
    @property
    def value(self) -> TValue:
        return self.__value

    @property
    def policy(self) -> CacheEntryPolicy:
        return self.__policy

    def __init__(
        self,
        value: TValue,
        policy: CacheEntryPolicy
    ) -> None:
        super().__init__()
        self.__value = value
        self.__policy = policy

class _ItemStore(IAsyncDisposable, Generic[TKey, TValue]):
    def __init__(
        self,
        cleanup_interval: timedelta,
        logger: ILogger
    ) -> None:
        super().__init__()
        if cleanup_interval < ZERO_TIMEDELTA:
            raise ArgumentError("cleanup_interval", "Value must be positive.")

        self.__logger = logger
        self.__entries = dict[_CacheEntryKey[TKey], _CacheEntry[TValue]]()
        self.__expires = dict[_CacheEntryKey[TKey], _CacheEntry[TValue]]()
        # TODO Async reader-writer lock?
        self.__lock = asyncio.Lock()
        self.__token_source = CancellationTokenSource()
        self.__background_task = asyncio.create_task(
            self.__remove_expired_entries(cleanup_interval, self.__token_source.token)
        )

    async def get(self, key: _CacheEntryKey[TKey]) -> TValue | UndefinedType:
        async with self.__lock:
            return self.__get_entry(key)

    async def get_or_add(
        self,
        key: _CacheEntryKey[TKey],
        value_or_factory: TValue | Callable[[TKey], Awaitable[TValue]],
        policy: CacheEntryPolicy
    ) -> TValue | UndefinedType:
        if policy.is_expired():
            return UNDEFINED

        async with self.__lock:
            entry = self.__get_entry(key)
            if not isinstance(entry, UndefinedType):
                return entry

            value = (
                await value_or_factory(key.key)
                if isinstance(value_or_factory, Callable)
                else value_or_factory
            )

            # Ignoring type-checking below, because for some reason
            # the wrong types are inferred.
            entry = _CacheEntry(value, policy)
            self.__entries[key] = entry # type:ignore

            if not isinstance(policy, NoExpirationCacheEntryPolicy):
                self.__expires[key] = entry # type:ignore

            return entry.value

    async def add_or_replace(
        self,
        key: _CacheEntryKey[TKey],
        value: TValue,
        policy: CacheEntryPolicy
    ) -> TValue | UndefinedType:
        if policy.is_expired():
            return UNDEFINED

        async with self.__lock:
            self.__remove_entry(key, True)

            entry = _CacheEntry(value, policy)
            self.__entries[key] = entry

            if not isinstance(policy, NoExpirationCacheEntryPolicy):
                self.__expires[key] = entry

            return entry.value

    async def remove(
        self,
        key: _CacheEntryKey[TKey]
    ) -> TValue | UndefinedType:
        async with self.__lock:
            return self.__remove_entry(key, False)

    async def _on_dispose(self) -> None:
        if self.__token_source: self.__token_source.cancel()
        try:
            await self.__background_task
        except asyncio.exceptions.CancelledError:
            pass

    def __get_entry(self, key: _CacheEntryKey[TKey]) -> TValue | UndefinedType:
        entry = self.__entries.get(key, UNDEFINED)
        if isinstance(entry, UndefinedType):
            return UNDEFINED

        if entry.policy.is_expired():
            self.__remove_entry(key, True)
            return UNDEFINED

        entry.policy.on_entry_accessed()

        return entry.value

    def __remove_entry(
        self,
        key: _CacheEntryKey[TKey],
        dispose_value: bool
    ) -> TValue | UndefinedType:
        value = self.__entries.pop(key, None)
        value2 = self.__expires.pop(key, None)

        if value is not None:
            self.__try_dispose_entry(value)
            return value.value

        if value2 is not None:
            self.__try_dispose_entry(value2)
            return value2.value

        return UNDEFINED

    async def __remove_expired_entries(self, interval: timedelta, token: CancellationToken):
        while not token.is_cancellation_requested:
            # Waiting immediately, because the cache is empty on creation.
            await wait(interval, token)

            for key in list(self.__expires.keys()):
                if (
                    isinstance(entry := self.__expires.get(key, UNDEFINED), UndefinedType)
                    or not entry.policy.is_expired()
                ):
                    continue

                self.__remove_entry(key, True)

    def __try_dispose_entry(self, entry: Any) -> None:
        # Can't type-check against a Protocol at runtime,
        # so quick-check if there is a suitable-ish method.
        try:
            if entry is not None and hasattr(entry, "dispose"):
                cast(IDisposable, entry).dispose()
        except Exception as error:
            self.__logger.error("Failed to dispose cache entry", error)

_DEFAULT_NO_EXPIRATION_POLICY = NoExpirationCacheEntryPolicy()

class ConcurrentMemoryCache(ICache, IAsyncDisposable, Generic[TKey, TValue]):
    """Default implementation of an in-memory cache that supports concurrent access."""

    def __init__(
        self,
        logger_factory: ILoggerFactory,
        cleanup_interval: timedelta | None = None
    ):
        logger = logger_factory.create(ConcurrentMemoryCache)
        self.__stores = tuple(
            _ItemStore[TKey, TValue](
                cleanup_interval or DEFAULT_CLEANUP_INTERVAL,
                logger
            )
            for _ in range(DEGREE_OF_PARALLELISM)
        )

    async def _on_dispose(self) -> None:
        for store in self.__stores:
            await store.dispose()

    async def get(self, key: TKey) -> TValue | UndefinedType:
        cache_key = _CacheEntryKey(key)
        store = self.__get_store(cache_key)
        return await store.get(cache_key)

    async def get_or_add(
        self,
        key: TKey,
        value_or_factory: TValue | Callable[[TKey], Awaitable[TValue]],
        policy: CacheEntryPolicy | None = None
    ) -> TValue | UndefinedType:
        if not policy:
            policy = _DEFAULT_NO_EXPIRATION_POLICY

        if policy.is_expired():
            return UNDEFINED

        cache_key = _CacheEntryKey(key)
        store = self.__get_store(cache_key)
        return await store.get_or_add(cache_key, value_or_factory, policy)

    async def add_or_replace(
        self,
        key: TKey,
        value: TValue,
        policy: CacheEntryPolicy | None = None
    ) -> TValue | UndefinedType:
        if not policy:
            policy = _DEFAULT_NO_EXPIRATION_POLICY

        cache_key = _CacheEntryKey(key)
        store = self.__get_store(cache_key)
        if policy.is_expired():
            await store.remove(cache_key)
            return UNDEFINED

        return await store.add_or_replace(cache_key, value, policy)

    def remove(self, key: TKey) -> Awaitable[TValue | UndefinedType]:
        cache_key = _CacheEntryKey(key)
        store = self.__get_store(cache_key)

        return store.remove(cache_key)

    def __get_store(self, key: _CacheEntryKey[TKey]) -> _ItemStore[TKey, TValue]:
        index = key.hash_value % len(self.__stores)
        return self.__stores[index]
