from collections.abc import Awaitable
from typing import Protocol

from holobot.sdk.database.enums import IsolationLevel
from .iunit_of_work import IUnitOfWork

class IUnitOfWorkProvider(Protocol):
    """Interface for a service used to access units of work."""

    @property
    def current(self) -> IUnitOfWork | None:
        """Gets the current unit of work.

        :return: If exists, the current unit of work; otherwise, None.
        :rtype: IUnitOfWork | None
        """
        ...

    def create_new(
        self,
        isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED
    ) -> Awaitable[IUnitOfWork]:
        """Creates a new unit of work.

        :return: The new unit of work.
        :rtype: Awaitable[IUnitOfWork]
        """
        ...
