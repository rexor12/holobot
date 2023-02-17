from collections.abc import Awaitable
from typing import Protocol

from .isession import ISession

class IDatabaseManager(Protocol):
    def upgrade_all(self) -> Awaitable[None]:
        ...

    def downgrade_many(self, version_by_table: tuple[str, int]) -> Awaitable[None]:
        ...

    def acquire_connection(self) -> Awaitable[ISession]:
        ...
