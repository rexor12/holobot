from asyncpg.connection import Connection

from holobot.sdk.database.migration import MigrationBase, MigrationInterface
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

TABLE_NAME = "moderation_mutes"

@injectable(MigrationInterface)
class MutesMigration(MigrationBase):
    def __init__(self):
        super().__init__(TABLE_NAME, {
            0: MigrationPlan(0, 1, self.__initialize_table),
            1: MigrationPlan(1, 2, self.__upgrade_to_v2)
        }, {})

    async def __upgrade_to_v2(self, connection: Connection) -> None:
        await connection.execute(f"DROP TABLE {TABLE_NAME}")

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
        await connection.execute((
            f"CREATE TABLE {TABLE_NAME} ("
            " id SERIAL PRIMARY KEY,"
            " modified_at TIMESTAMP DEFAULT (NOW() at time zone 'utc'),"
            " server_id VARCHAR(20) NOT NULL,"
            " user_id VARCHAR(20) NOT NULL,"
            " expires_at TIMESTAMP NOT NULL,"
            " UNIQUE(server_id, user_id)"
            " )"
        ))
