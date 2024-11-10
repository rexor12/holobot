from asyncpg.connection import Connection

from holobot.sdk.database.migration import IMigration, MigrationBase
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(IMigration)
class ReputationCooldownsMigration(MigrationBase):
    def __init__(self) -> None:
        super().__init__(
            "reputation_cooldowns",
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
            " ALTER COLUMN id TYPE BIGINT USING id::BIGINT,\n"
            " ALTER COLUMN last_target_user_id TYPE BIGINT USING last_target_user_id::BIGINT"
        )

        await connection.execute(f"ALTER TABLE {self.table_name} ADD PRIMARY KEY (id)")

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute((
            f"CREATE TABLE {self.table_name} ("
            " id VARCHAR(20) PRIMARY KEY,\n"
            " last_target_user_id VARCHAR(20) NOT NULL,\n"
            " last_rep_at TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc')\n"
            ")"
        ))
