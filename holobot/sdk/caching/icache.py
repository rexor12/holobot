from collections.abc import Awaitable, Callable
from typing import Protocol, TypeVar

from holobot.sdk.utils.type_utils import UndefinedType
from .cache_entry_policy import CacheEntryPolicy

TKey = TypeVar("TKey")
TValue = TypeVar("TValue")

class ICache(Protocol[TKey, TValue]):
    """Interface for a cache."""

    def get(self, key: TKey) -> Awaitable[TValue | UndefinedType]:
        """Gets the item with the given key, if exists.

        :param key: The key that identifies the item.
        :type key: TKey
        :return: If found, the associated value; otherwise, an undefined.
        :rtype: Awaitable[TValue | UndefinedType]
        """
        ...

    def get_or_add(
        self,
        key: TKey,
        value_or_factory: TValue | Callable[[TKey], Awaitable[TValue]],
        policy: CacheEntryPolicy | None = None
    ) -> Awaitable[TValue | UndefinedType]:
        """Gets the item with the given key, if exists; otherwise adds it.

        Note: Expiring objects are automatically disposed if they implement
        the IDisposable interface.

        :param key: The key that identifies the item.
        :type key: TKey
        :param value_or_factory: A factory method that creates the value, or the value itself, to be added.
        :type value_or_factory: TValue | Callable[[TKey], Awaitable[TValue]]
        :param policy: The eviction policy for this item, defaults to None
        :type policy: CacheEntryPolicy | None, optional
        :return: The found or newly added item, if valid; otherwise, an undefined.
        :rtype: Awaitable[TValue | UndefinedType]
        """
        ...

    def add_or_replace(
        self,
        key: TKey,
        value: TValue,
        policy: CacheEntryPolicy | None = None
    ) -> Awaitable[TValue | UndefinedType]:
        """Adds the specified value or replaces the existing one.

        Note: The replaced object is automatically disposed if it implements
        the IDisposable interface.

        :param key: The key that identifies the item.
        :type key: TKey
        :param value: The value to be added.
        :type value: TValue
        :param policy: The eviction policy for this item, defaults to None
        :type policy: CacheEntryPolicy | None, optional
        :return: The newly added item, if valid; otherwise, an undefined.
        :rtype: Awaitable[TValue | UndefinedType]
        """
        ...

    def remove(self, key: TKey) -> Awaitable[TValue | UndefinedType]:
        """Removes the value associated to the specified key, if it exists.

        Note: The object must be disposed by the caller in this case.

        :param key: The key that identifies the item.
        :type key: TKey
        :return: The cached value, if exists; otherwise, an undefined.
        :rtype: Awaitable[TValue | UndefinedType]
        """
        ...
