from asyncpg.connection import Connection

from holobot.sdk.database.migration import IMigration, MigrationBase
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(IMigration)
class WarnsSettingsMigration(MigrationBase):
    def __init__(self):
        super().__init__(
            "moderation_warn_settings",
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
            " ALTER COLUMN server_id TYPE BIGINT USING server_id::BIGINT"
        )

        await connection.execute(
            f"ALTER TABLE {self.table_name}\n"
            " ADD CONSTRAINT uc_moderation_warn_settings_server_id UNIQUE (server_id)"
        )

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute(f"DROP TABLE IF EXISTS {self.table_name}")
        await connection.execute((
            f"CREATE TABLE {self.table_name} ("
            " id SERIAL PRIMARY KEY,"
            " modified_at TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'utc'),"
            " server_id VARCHAR(20) UNIQUE NOT NULL,"
            " decay_threshold INTERVAL DEFAULT NULL,"
            " auto_mute_after INTEGER NOT NULL DEFAULT 0,"
            " auto_mute_duration INTERVAL DEFAULT NULL,"
            " auto_kick_after INTEGER NOT NULL DEFAULT 0,"
            " auto_ban_after INTEGER NOT NULL DEFAULT 0"
            " )"
        ))
