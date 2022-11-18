from collections.abc import Callable
from typing import Protocol, TypeVar

from holobot.sdk.utils.type_utils import UndefinedType
from .cache_entry_policy import CacheEntryPolicy

TKey = TypeVar("TKey")
TValue = TypeVar("TValue")

class ICache(Protocol[TKey, TValue]):
    async def get(self, key: TKey) -> TValue | UndefinedType:
        ...

    async def get_or_add(
        self,
        key: TKey,
        value_or_factory: TValue | Callable[[TKey], TValue],
        policy: CacheEntryPolicy | None = None
    ) -> TValue | UndefinedType:
        ...

    async def add_or_replace(
        self,
        key: TKey,
        value: TValue,
        policy: CacheEntryPolicy | None = None
    ) -> TValue | UndefinedType:
        ...
