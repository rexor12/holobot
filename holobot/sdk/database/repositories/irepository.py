from collections.abc import Awaitable
from typing import Protocol, TypeVar

from holobot.sdk.database.entities import Identifier

TIdentifier = TypeVar("TIdentifier", bound=str | int | Identifier)
TModel = TypeVar("TModel")

class IRepository(Protocol[TIdentifier, TModel]):
    def add(self, model: TModel) -> Awaitable[TIdentifier]:
        """Adds a new entity to the repository.

        :param model: The model to be added.
        :type model: TModel
        :return: The identifier assigned to the entity.
        :rtype: Awaitable[TIdentifier]
        """
        ...

    def get(self, identifier: TIdentifier) -> Awaitable[TModel | None]:
        """Gets an entity from the repository.

        :param identifier: The identifier of the entity.
        :type identifier: TIdentifier
        :return: If exists, the entity associated to the identifier; otherwise, None.
        :rtype: Awaitable[TModel | None]
        """
        ...

    def get_all(self) -> Awaitable[tuple[TModel, ...]]:
        ...

    def count(self) -> Awaitable[int | None]:
        """Gets the number of entities that are present in the repository.

        :return: The number of existing entities.
        :rtype: Awaitable[int | None]
        """
        ...

    def update(self, model: TModel) -> Awaitable[bool]:
        """Updates an existing entity in the repository.

        :param model: The entity to be updated.
        :type model: TModel
        :return: True, if the entity exists and was successfully updated.
        :rtype: Awaitable[bool]
        """
        ...

    def delete(self, identifier: TIdentifier) -> Awaitable[int]:
        """Deletes an entity from the repository.

        :param identifier: The identifier of the entity.
        :type identifier: TIdentifier
        :return: The number of affected entities.
        :rtype: Awaitable[int]
        """
        ...
