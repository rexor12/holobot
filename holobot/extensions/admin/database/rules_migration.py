from asyncpg.connection import Connection

from holobot.sdk.database.migration import IMigration, MigrationBase
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(IMigration)
class RulesMigration(MigrationBase):
    def __init__(self):
        super().__init__(
            "admin_rules",
            [
                MigrationPlan(1, self.__initialize_table),
                MigrationPlan(2, self.__upgrade_to_v2),
                MigrationPlan(202411071725, self.__upgrade_to_v3)
            ]
        )

    async def __upgrade_to_v3(self, connection: Connection) -> None:
        await connection.execute(
            f"ALTER TABLE {self.table_name}"
            " ALTER COLUMN channel_id DROP DEFAULT"
        )

        await connection.execute(
            f"ALTER TABLE {self.table_name}\n"
            " ALTER COLUMN server_id TYPE BIGINT USING server_id::BIGINT,\n"
            " ALTER COLUMN channel_id TYPE BIGINT USING channel_id::BIGINT,\n"
            " ALTER COLUMN created_by TYPE BIGINT USING created_by::BIGINT"
        )

        await connection.execute(
            f"ALTER TABLE {self.table_name}"
            " ALTER COLUMN channel_id SET DEFAULT NULL"
        )

    async def __upgrade_to_v2(self, connection: Connection) -> None:
        await connection.execute((
            f"ALTER TABLE {self.table_name}"
            " ADD COLUMN command_subgroup VARCHAR(25) DEFAULT NULL"
        ))

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute(f"DROP TABLE IF EXISTS {self.table_name}")
        await connection.execute((
            f"CREATE TABLE {self.table_name} ("
            " id SERIAL PRIMARY KEY,"
            " created_at TIMESTAMP DEFAULT NOW(),"
            " created_by VARCHAR(20) NOT NULL,"
            " server_id VARCHAR(20) NOT NULL,"
            " state SMALLINT DEFAULT 0,"
            " command_group VARCHAR(25) DEFAULT NULL,"
            " command VARCHAR(25) DEFAULT NULL,"
            " channel_id VARCHAR(20) DEFAULT NULL"
            " )"
        ))
