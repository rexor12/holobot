from asyncpg.connection import Connection

from holobot.sdk.database.migration import IMigration, MigrationBase
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(IMigration)
class MudadaTransactionsMigration(MigrationBase):
    _TABLE_NAME = "mudada_transactions"

    def __init__(self) -> None:
        super().__init__(
            MudadaTransactionsMigration._TABLE_NAME,
            [
                MigrationPlan(1, self.__initialize_table),
                MigrationPlan(202411071725, self.__upgrade_to_v2)
            ]
        )

    async def __upgrade_to_v2(self, connection: Connection) -> None:
        uc_name = await self._query_unique_constraint_name(connection, self.table_name)
        await connection.execute(f"ALTER TABLE {self.table_name} DROP CONSTRAINT {uc_name}")

        await connection.execute(
            f"ALTER TABLE {self.table_name}\n"
            " ALTER COLUMN owner_id TYPE BIGINT USING owner_id::BIGINT,\n"
            " ALTER COLUMN target_id TYPE BIGINT USING target_id::BIGINT"
        )

        await connection.execute(
            f"ALTER TABLE {self.table_name}\n"
            " ADD CONSTRAINT uc_mudada_transactions_owner_id_target_id UNIQUE (owner_id, target_id)"
        )

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute((
            f"CREATE TABLE {MudadaTransactionsMigration._TABLE_NAME} ("
            " id SERIAL PRIMARY KEY,\n"
            " created_at TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),\n"
            " owner_id VARCHAR(20) NOT NULL,\n"
            " target_id VARCHAR(20) NOT NULL,\n"
            " amount INTEGER NOT NULL,\n"
            " message VARCHAR(120) DEFAULT NULL,\n"
            " is_finalized BOOLEAN DEFAULT false,\n"
            " is_completed BOOLEAN DEFAULT false,\n"
            " UNIQUE(owner_id, target_id)\n"
            ")"
        ))
