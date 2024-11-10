from asyncpg.connection import Connection

from holobot.sdk.database.migration import IMigration, MigrationBase
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(IMigration)
class LogSettingsMigration(MigrationBase):
    def __init__(self):
        super().__init__(
            "moderation_log_settings",
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
            " ALTER COLUMN server_id TYPE BIGINT USING server_id::BIGINT,\n"
            " ALTER COLUMN channel_id TYPE BIGINT USING channel_id::BIGINT"
        )

        await connection.execute(
            f"ALTER TABLE {self.table_name}\n"
            " ADD CONSTRAINT uc_moderation_log_settings_server_id UNIQUE (server_id)"
        )

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute(f"DROP TABLE IF EXISTS {self.table_name}")
        await connection.execute((
            f"CREATE TABLE {self.table_name} ("
            " id SERIAL PRIMARY KEY,"
            " modified_at TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'utc'),"
            " server_id VARCHAR(20) UNIQUE NOT NULL,"
            " channel_id VARCHAR(20) NOT NULL"
            " )"
        ))
