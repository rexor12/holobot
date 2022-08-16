from asyncpg.pool import PoolAcquireContext

class DatabaseManagerInterface:
    async def upgrade_all(self):
        raise NotImplementedError

    async def downgrade_many(self, version_by_table: tuple[str, int]):
        raise NotImplementedError

    # TODO Abstract PostgreSQL away.
    def acquire_connection(self) -> PoolAcquireContext:
        raise NotImplementedError
