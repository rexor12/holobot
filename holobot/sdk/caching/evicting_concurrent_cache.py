import asyncio
import os
from abc import ABCMeta, abstractmethod
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Generic, TypeVar

from holobot.sdk.concurrency import IAsyncDisposable
from holobot.sdk.exceptions import ArgumentError
from holobot.sdk.threading import CancellationToken, CancellationTokenSource
from holobot.sdk.threading.utils import wait
from holobot.sdk.utils import UNDEFINED, UndefinedType
from holobot.sdk.utils.datetime_utils import utcnow
from holobot.sdk.utils.timedelta_utils import ZERO_TIMEDELTA

TKey = TypeVar("TKey")
TValue = TypeVar("TValue")

# On most Linux systems, sched_getaffinity returns the number of processor cores
# available to the executing Python process. When unavailable, we fall back to 4.
DEGREE_OF_PARALLELISM = (
    os.sched_getaffinity(0) # type: ignore
    if hasattr(os, "sched_getaffinity")
    else 4
)

DEFAULT_CLEANUP_INTERVAL = timedelta(seconds=20)

class CacheEntryPolicy(metaclass=ABCMeta):
    @abstractmethod
    def is_expired(self) -> bool:
        ...

    def on_entry_accessed(self) -> None:
        pass

class NoExpirationCacheEntryPolicy(CacheEntryPolicy):
    def is_expired(self) -> bool:
        return False

class AbsoluteExpirationCacheEntryPolicy(CacheEntryPolicy):
    @property
    def expires_at(self) -> datetime:
        return self.__expires_at

    def __init__(
        self,
        expires_at: datetime
    ) -> None:
        super().__init__()
        self.__expires_at = expires_at

    def is_expired(self) -> bool:
        return utcnow() >= self.__expires_at

class SlidingExpirationCacheEntryPolicy(CacheEntryPolicy):
    @property
    def expires_after(self) -> timedelta:
        return self.__expires_after

    @property
    def expires_at(self) -> datetime:
        return self.__expires_at

    def __init__(
        self,
        expires_after: timedelta
    ) -> None:
        super().__init__()
        self.__expires_after = expires_after
        self.__expires_at = utcnow() + expires_after

    def is_expired(self) -> bool:
        return utcnow() >= self.__expires_at

    def on_entry_accessed(self) -> None:
        self.__expires_at = utcnow() + self.__expires_after

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

class _ItemStore(Generic[TKey, TValue], IAsyncDisposable):
    def __init__(
        self,
        cleanup_interval: timedelta
    ) -> None:
        super().__init__()
        if cleanup_interval < ZERO_TIMEDELTA:
            raise ArgumentError("cleanup_interval", "Value must be positive.")

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
        value_or_factory: TValue | Callable[[TKey], TValue],
        policy: CacheEntryPolicy
    ) -> TValue | UndefinedType:
        if policy.is_expired():
            return UNDEFINED

        async with self.__lock:
            entry = self.__get_entry(key)
            if not isinstance(entry, UndefinedType):
                return entry

            value = (
                value_or_factory(key.key)
                if isinstance(value_or_factory, Callable)
                else value_or_factory
            )
            entry = _CacheEntry(value, policy)
            self.__entries[key] = entry

            if not isinstance(policy, NoExpirationCacheEntryPolicy):
                self.__expires[key] = entry

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
            self.__remove_entry(key)

            entry = _CacheEntry(value, policy)
            self.__entries[key] = entry

            if not isinstance(policy, NoExpirationCacheEntryPolicy):
                self.__expires[key] = entry

            return entry.value

    async def remove(
        self,
        key: _CacheEntryKey[TKey]
    ) -> None:
        async with self.__lock:
            self.__remove_entry(key)

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
            self.__remove_entry(key)
            return UNDEFINED

        entry.policy.on_entry_accessed()

        return entry.value

    def __remove_entry(self, key: _CacheEntryKey[TKey]) -> None:
        self.__entries.pop(key, None)
        self.__expires.pop(key, None)

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

                self.__remove_entry(key)

_DEFAULT_NO_EXPIRATION_POLICY = NoExpirationCacheEntryPolicy()

class EvictingConcurrentCache(Generic[TKey, TValue], IAsyncDisposable):
    def __init__(
        self,
        cleanup_interval: timedelta | None = None
    ):
        self.__stores = tuple(
            _ItemStore[TKey, TValue](cleanup_interval or DEFAULT_CLEANUP_INTERVAL)
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
        value_or_factory: TValue | Callable[[TKey], TValue],
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

    def __get_store(self, key: _CacheEntryKey[TKey]) -> _ItemStore:
        index = key.hash_value % len(self.__stores)
        return self.__stores[index]
