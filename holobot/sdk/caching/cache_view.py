from collections.abc import Awaitable, Callable
from typing import Any, Generic, TypeVar

from holobot.sdk.utils.type_utils import UndefinedType
from .cache_entry_policy import CacheEntryPolicy
from .icache import ICache

TKey = TypeVar("TKey")
TValue = TypeVar("TValue")

class CacheView(Generic[TKey, TValue]):
    """A view of a cache with specific key and value types."""

    def __init__(
        self,
        value_type: type[TValue],
        parent: ICache[Any, Any]
    ) -> None:
        super().__init__()
        self.__value_type = value_type
        self.__parent = parent

    async def get(self, key: TKey) -> TValue | UndefinedType:
        """Gets the item with the given key, if exists.

        :param key: The key that identifies the item.
        :type key: TKey
        :raises TypeError: Raised when the item with the given key is of an unexpected type.
        :return: If found, the associated value; otherwise, an undefined.
        :rtype: TValue | UndefinedType
        """

        value = await self.__parent.get(key)
        if isinstance(value, UndefinedType):
            return value

        if not isinstance(value, self.__value_type):
            raise TypeError(
                f"The cache item associated to the key '{key}' was expected to be of type"
                f" '{self.__value_type}', but it is of type '{type(value)}'."
            )

        return value

    async def get_or_add(
        self,
        key: TKey,
        value_or_factory: TValue | Callable[[TKey], Awaitable[TValue]],
        policy: CacheEntryPolicy | None = None
    ) -> TValue | UndefinedType:
        """Gets the item with the given key, if exists; otherwise adds it.

        :param key: The key that identifies the item.
        :type key: TKey
        :param value_or_factory: A factory method that creates the value , or the value itself, to be added.
        :type value_or_factory: TValue | Callable[[TKey], Awaitable[TValue]]
        :param policy: The eviction policy for this item, defaults to None
        :type policy: CacheEntryPolicy | None, optional
        :raises TypeError: Raised when the item with the given key is of an unexpected type.
        :return: The found or newly added item, if valid; otherwise, an undefined.
        :rtype: TValue | UndefinedType
        """

        value = await self.__parent.get_or_add(
            key,
            value_or_factory,
            policy
        )

        if not isinstance(value, self.__value_type):
            raise TypeError(
                f"The cache item associated to the key '{key}' was expected to be of type"
                f" '{self.__value_type}', but it is of type '{type(value)}'."
            )

        return value

    async def add_or_replace(
        self,
        key: TKey,
        value: TValue,
        policy: CacheEntryPolicy | None = None
    ) -> TValue | UndefinedType:
        """Adds the specified item or replaces the existing one.

        :param key: The key that identifiers the item.
        :type key: TKey
        :param value: The item to be added.
        :type value: TValue
        :param policy: The eviction policy for this item, defaults to None
        :type policy: CacheEntryPolicy | None, optional
        :raises TypeError: Raised when the item with the given key is of an unexpected type.
        :return: The newly added item, if valid; otherwise, an undefined.
        :rtype: TValue | UndefinedType
        """

        resulting_value = await self.__parent.add_or_replace(
            key,
            value,
            policy
        )

        if not isinstance(resulting_value, self.__value_type):
            raise TypeError(
                f"The cache item associated to the key '{key}' was expected to be of type"
                f" '{self.__value_type}', but it is of type '{type(resulting_value)}'."
            )

        return resulting_value
