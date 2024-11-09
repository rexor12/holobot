from collections.abc import Awaitable
from typing import Protocol

from .isession import ISession

class IDatabaseManager(Protocol):
    def upgrade_all(self) -> Awaitable[None]:
        ...

    def acquire_connection(self) -> Awaitable[ISession]:
        ...
