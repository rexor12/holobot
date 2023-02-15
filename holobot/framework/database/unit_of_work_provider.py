import contextvars
from collections.abc import Awaitable

from asyncpg import Connection
from asyncpg.pool import PoolAcquireContext

from holobot.sdk.database import IDatabaseManager, IUnitOfWork, IUnitOfWorkProvider
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.ioc.decorators import injectable
from .unit_of_work import UnitOfWork

@injectable(IUnitOfWorkProvider)
class UnitOfWorkProvider(IUnitOfWorkProvider):
    """Default implementation of a service used to access units of work."""

    def __init__(
        self,
        database_manager: IDatabaseManager
    ) -> None:
        super().__init__()
        self.__database_manager = database_manager
        self.__unit_of_work = contextvars.ContextVar[IUnitOfWork | None](
            "unit_of_work",
            default=None
        )

    @property
    def current(self) -> IUnitOfWork | None:
        return self.__unit_of_work.get()

    async def create_new(self) -> IUnitOfWork:
        if self.__unit_of_work.get():
            raise InvalidOperationError("Nesting of units of work is not supported.")

        context = self.__database_manager.acquire_connection()
        connection: Connection = await context.__aenter__()
        transaction = connection.transaction()
        await transaction.start()

        unit_of_work = UnitOfWork(
            connection,
            transaction,
            lambda: self.__remove_unit_of_work(context)
        )
        self.__unit_of_work.set(unit_of_work)

        return unit_of_work

    def __remove_unit_of_work(
        self,
        context: PoolAcquireContext
    ) -> Awaitable[None]:
        self.__unit_of_work.set(None)
        return context.__aexit__()
