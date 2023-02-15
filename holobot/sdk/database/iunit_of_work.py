from abc import abstractmethod
from collections.abc import Awaitable
from typing import Any, TypeVar

from asyncpg import Connection

from holobot.sdk.concurrency import IAsyncDisposable
from .aggregate_root import AggregateRoot

TIdentifier = TypeVar("TIdentifier")

class IUnitOfWork(IAsyncDisposable):
    """Interface for a unit of work."""

    @property
    @abstractmethod
    def connection(self) -> Connection:
        """Gets the connection the unit of work belongs to.

        :return: The owning connection.
        :rtype: Connection
        """

    @abstractmethod
    def complete(self) -> None:
        """Completes the unit of work."""

    @abstractmethod
    def get(
        self,
        entity_type: type[AggregateRoot[TIdentifier]],
        identifier: TIdentifier
    ) -> Awaitable[Any | None]:
        """Gets the entity with the specified identifier.

        :param entity_type: The type of the entity.
        :type entity_type: type[AggregateRoot[TIdentifier]]
        :param identifier: The identifier of the entity.
        :type identifier: TIdentifier
        :return: If found, the matching entity; otherwise, None.
        :rtype: Awaitable[Any | None]
        """

    @abstractmethod
    def set(
        self,
        value: AggregateRoot[Any]
    ) -> Awaitable[None]:
        """Sets the specified entity.

        If there is already an entity with the same identifier,
        this new entity will replace the old one.

        :param identifier: The identifier of the entity.
        :type identifier: TIdentifier
        :param value: The entity to be set.
        :type value: AggregateRoot[Any]
        :return: None.
        :rtype: Awaitable[None]
        """

    @abstractmethod
    def remove(
        self,
        entity_type: type[AggregateRoot[TIdentifier]],
        identifier: TIdentifier
    ) -> Awaitable[None]:
        """Removes the entity with the specified identifier.

        :param entity_type: The type of the entity.
        :type entity_type: type[AggregateRoot[TIdentifier]]
        :param identifier: The identifier of the entity.
        :type identifier: TIdentifier
        :return: None.
        :rtype: Awaitable[None]
        """

    @abstractmethod
    async def _on_dispose(self) -> None:
        ...
