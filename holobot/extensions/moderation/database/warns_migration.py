from asyncpg.connection import Connection

from holobot.sdk.database.migration import IMigration, MigrationBase
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(IMigration)
class WarnsMigration(MigrationBase):
    def __init__(self):
        super().__init__(
            "moderation_warns",
            [
                MigrationPlan(1, self.__initialize_table),
                MigrationPlan(202411071725, self.__upgrade_to_v2)
            ]
        )

    async def __upgrade_to_v2(self, connection: Connection) -> None:
        await connection.execute(
            f"ALTER TABLE {self.table_name}\n"
            " ALTER COLUMN server_id TYPE BIGINT USING server_id::BIGINT,\n"
            " ALTER COLUMN user_id TYPE BIGINT USING user_id::BIGINT,\n"
            " ALTER COLUMN warner_id TYPE BIGINT USING warner_id::BIGINT"
        )

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute(f"DROP TABLE IF EXISTS {self.table_name}")
        await connection.execute((
            f"CREATE TABLE {self.table_name} ("
            " id SERIAL PRIMARY KEY,"
            " created_at TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'utc'),"
            " server_id VARCHAR(20) NOT NULL,"
            " user_id VARCHAR(20) NOT NULL,"
            " reason VARCHAR(192) NOT NULL,"
            " warner_id VARCHAR(20) NOT NULL"
            " )"
        ))
