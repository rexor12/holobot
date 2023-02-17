import contextvars
from collections.abc import Awaitable

from holobot.sdk.database import IDatabaseManager, ISession, IUnitOfWork, IUnitOfWorkProvider
from holobot.sdk.database.enums import IsolationLevel
from holobot.sdk.exceptions import ArgumentError, InvalidOperationError
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

    async def create_new(
        self,
        isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED
    ) -> IUnitOfWork:
        if self.__unit_of_work.get():
            raise InvalidOperationError("Nesting of units of work is not supported.")

        pg_isolation_level = UnitOfWorkProvider.__get_pg_isolation_level(isolation_level)
        session = await self.__database_manager.acquire_connection()
        try:
            transaction = session.connection.transaction(isolation=pg_isolation_level)
            await transaction.start()

            unit_of_work = UnitOfWork(
                session.connection,
                transaction,
                lambda: self.__remove_unit_of_work(session)
            )
            self.__unit_of_work.set(unit_of_work)

            return unit_of_work
        except:
            await session.dispose()
            raise

    def __remove_unit_of_work(
        self,
        session: ISession
    ) -> Awaitable[None]:
        self.__unit_of_work.set(None)
        return session.dispose()

    @staticmethod
    def __get_pg_isolation_level(isolation_level: IsolationLevel) -> str:
        match isolation_level:
            case IsolationLevel.SERIALIZABLE:
                return "serializable"
            case IsolationLevel.READ_COMMITTED:
                return "read_committed"
            case _:
                raise ArgumentError(
                    "isolation_level",
                    "The specified value is not a valid isolation level."
                )
