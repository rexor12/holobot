from collections.abc import Awaitable
from typing import Protocol, TypeVar

from holobot.sdk.database.aggregate_root import AggregateRoot

_TIdentifier = TypeVar("_TIdentifier", int, str)
_TEntity = TypeVar("_TEntity", bound=AggregateRoot)

class IEntityCache(Protocol):
    """Interface for an entity cache.

    Entities may be added to the cache manually, in which case invalidation also
    must be performed manually, when necessary.
    """

    def get(self, entity_type: type[_TEntity], identifier: _TIdentifier) -> Awaitable[_TEntity | None]:
        """Gets the entity of the specified type with the specified identifier.

        :param entity_type: The type of the entity.
        :type entity_type: type[_TEntity]
        :param identifier: The identifier of the entity.
        :type identifier: _TIdentifier
        :return: If found, the matching entity; otherwise, None.
        :rtype: Awaitable[_TEntity | None]
        """
        ...

    def set(self, entity: AggregateRoot[_TIdentifier]) -> Awaitable[None]:
        """Starts tracking the specified entity.

        :param entity: The entity to be tracked.
        :type entity: AggregateRoot[_TIdentifier]
        :return: None
        :rtype: Awaitable[None]
        """
        ...

    def invalidate(self, entity_type: type[_TEntity], identifier: _TIdentifier) -> Awaitable[None]:
        """Invalidates the entity of the specified type with the specified identifier.

        :param entity_type: The type of the entity.
        :type entity_type: type[_TEntity]
        :param identifier: The identifier of the entity.
        :type identifier: _TIdentifier
        :return: None
        :rtype: Awaitable[None]
        """
        ...
