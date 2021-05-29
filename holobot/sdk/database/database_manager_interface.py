from asyncpg.pool import PoolAcquireContext
from typing import Tuple

class DatabaseManagerInterface:
    async def upgrade_all(self):
        raise NotImplementedError

    async def downgrade_many(self, version_by_table: Tuple[str, int]):
        raise NotImplementedError
    
    # TODO Abstract PostgreSQL away.
    def acquire_connection(self) -> PoolAcquireContext:
        raise NotImplementedError
