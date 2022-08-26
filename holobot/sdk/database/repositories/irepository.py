from typing import Protocol, TypeVar

TIdentifier = TypeVar("TIdentifier")
TModel = TypeVar("TModel")

class IRepository(Protocol[TIdentifier, TModel]):
    async def add(self, model: TModel) -> TIdentifier:
        """Adds a new entity to the repository.

        :param model: The model to be added.
        :type model: TModel
        :return: The identifier assigned to the entity.
        :rtype: TIdentifier
        """
        ...

    async def get(self, identifier: TIdentifier) -> TModel | None:
        """Gets an entity from the repository.

        :param identifier: The identifier of the entity.
        :type identifier: TIdentifier
        :return: If exists, the entity associated to the identifier; otherwise, None.
        :rtype: TModel | None
        """
        ...

    async def count(self) -> int | None:
        """Gets the number of entities that are present in the repository.

        :return: The number of existing entities.
        :rtype: int | None
        """
        ...

    async def update(self, model: TModel) -> bool:
        """Updates an existing entity in the repository.

        :param model: The entity to be updated.
        :type model: TModel
        :return: True, if the entity exists and was successfully updated.
        :rtype: bool
        """
        ...

    async def delete(self, identifier: TIdentifier) -> int:
        """Deletes an entity from the repository.

        :param identifier: The identifier of the entity.
        :type identifier: TIdentifier
        :return: The number of affected entities.
        :rtype: int
        """
        ...
