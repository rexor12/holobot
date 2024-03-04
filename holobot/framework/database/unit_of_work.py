from collections.abc import Awaitable, Callable
from typing import Any

from asyncpg import Connection
from asyncpg.transaction import Transaction

from holobot.sdk.caching import ConcurrentDict
from holobot.sdk.database.entities import AggregateRoot
from holobot.sdk.database.iunit_of_work import IUnitOfWork, TIdentifier
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.threading.utils import as_task
from holobot.sdk.utils import UndefinedType

class UnitOfWork(IUnitOfWork):
    """Default implementation of a unit of work."""

    def __init__(
        self,
        connection: Connection,
        transaction: Transaction,
        on_disposed: Callable[[], Awaitable[None]]
    ) -> None:
        super().__init__()
        self.__connection = connection
        self.__transaction = transaction
        self.__on_disposed = on_disposed
        self.__is_completed = False
        self.__is_disposed = False
        self.__entities = ConcurrentDict[type, ConcurrentDict[str, Any]]()

    @property
    def connection(self) -> Connection:
        return self.__connection

    def complete(self) -> None:
        self.__throw_if_disposed()
        self.__is_completed = True

    async def get(
        self,
        entity_type: type[AggregateRoot[TIdentifier]],
        identifier: TIdentifier
    ) -> Any | None:
        self.__throw_if_disposed()
        if (
            isinstance(entities := await self.__entities.get(entity_type), UndefinedType)
            or isinstance(entity := await entities.get(str(identifier)), UndefinedType)
        ):
            return None

        return entity

    async def set(
        self,
        value: AggregateRoot[Any]
    ) -> None:
        self.__throw_if_disposed()
        entities = await self.__entities.get_or_add(
            type(value),
            lambda _: as_task(ConcurrentDict())
        )
        await entities.add_or_update(
            str(value.identifier),
            lambda _k: as_task(value),
            lambda _k, _v: as_task(value)
        )

    async def remove(
        self,
        entity_type: type[AggregateRoot[TIdentifier]],
        identifier: TIdentifier
    ) -> None:
        self.__throw_if_disposed()
        if isinstance(entities := await self.__entities.get(entity_type), UndefinedType):
            return

        await entities.remove(str(identifier))

    async def _on_dispose(self) -> None:
        if self.__is_disposed:
            return

        self.__is_disposed = True
        try:
            if not self.__is_completed:
                await self.__transaction.rollback()
                return

            await self.__transaction.commit()
        finally:
            await self.__on_disposed()

    def __throw_if_disposed(self) -> None:
        if self.__is_disposed:
            raise InvalidOperationError("The unit of work has been completed already.")
