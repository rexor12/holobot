from typing import Protocol

from asyncpg.pool import PoolAcquireContext

class IDatabaseManager(Protocol):
    async def upgrade_all(self):
        ...

    async def downgrade_many(self, version_by_table: tuple[str, int]):
        ...

    def acquire_connection(self) -> PoolAcquireContext:
        ...
