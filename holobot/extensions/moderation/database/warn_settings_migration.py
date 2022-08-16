from asyncpg.connection import Connection

from holobot.sdk.database.migration import MigrationBase, MigrationInterface
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

TABLE_NAME = "moderation_warn_settings"

@injectable(MigrationInterface)
class WarnsSettingsMigration(MigrationBase):
    def __init__(self):
        super().__init__(TABLE_NAME, {
            0: MigrationPlan(0, 1, self.__initialize_table)
        }, {})
    
    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
        await connection.execute((
            f"CREATE TABLE {TABLE_NAME} ("
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
