from typing import Any, Protocol, TypeVar

from .cache_view import CacheView
from .icache import ICache

TKey = TypeVar("TKey")
TValue = TypeVar("TValue")

class IObjectCache(ICache[Any, Any], Protocol):
    """Interface for a cache that can store any type of item."""

    def get_view(
        self,
        key_type: type[TKey],
        value_type: type[TValue]
    ) -> CacheView[TKey, TValue]:
        """Gets a view of the cache with specific key and value types.

        :param key_type: The type of the key.
        :type key_type: type[TKey]
        :param value_type: The type of the value.
        :type value_type: type[TValue]
        :return: A view of the cache.
        :rtype: CacheView[TKey, TValue]
        """
        ...
