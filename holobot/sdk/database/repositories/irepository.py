from typing import Protocol, TypeVar

TIdentifier = TypeVar("TIdentifier")
TModel = TypeVar("TModel")

class IRepository(Protocol[TIdentifier, TModel]):
    async def add(self, model: TModel) -> TIdentifier:
        ...

    async def get(self, identifier: TIdentifier) -> TModel | None:
        ...

    async def count(self) -> int | None:
        ...

    async def update(self, model: TModel) -> bool:
        ...

    async def delete(self, identifier: TIdentifier) -> int:
        ...
