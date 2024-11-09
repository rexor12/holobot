from asyncpg.connection import Connection

from holobot.sdk.database.migration import IMigration, MigrationBase
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(IMigration)
class MudadaExchangeQuotasMigration(MigrationBase):
    def __init__(self) -> None:
        super().__init__(
            "mudada_exchange_quotas",
            [
                MigrationPlan(1, self.__initialize_table),
                MigrationPlan(202411071725, self.__upgrade_to_v2)
            ]
        )

    async def __upgrade_to_v2(self, connection: Connection) -> None:
        pk_name = await self._query_primary_key_name(connection, self.table_name)
        await connection.execute(f"ALTER TABLE {self.table_name} DROP CONSTRAINT {pk_name}")

        await connection.execute(
            f"ALTER TABLE {self.table_name}\n"
            " ALTER COLUMN id TYPE BIGINT USING id::BIGINT"
        )

        await connection.execute(f"ALTER TABLE {self.table_name} ADD PRIMARY KEY (id)")

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute((
            f"CREATE TABLE {self.table_name} ("
            " id VARCHAR(20) PRIMARY KEY,\n"
            " amount INTEGER NOT NULL DEFAULT 0,\n"
            " exchanged_amount INTEGER NOT NULL DEFAULT 0,\n"
            " lost_amount INTEGER NOT NULL DEFAULT 0\n"
            ")"
        ))
