from asyncpg.connection import Connection

from holobot.sdk.database.migration import IMigration, MigrationBase
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(IMigration)
class ChannelTimerMigration(MigrationBase):
    def __init__(self) -> None:
        super().__init__(
            "channel_timers",
            [
                MigrationPlan(1, self.__initialize_table),
                MigrationPlan(202411071725, self.__upgrade_to_v2),
            ]
        )

    async def __upgrade_to_v2(self, connection: Connection) -> None:
        await connection.execute(
            f"ALTER TABLE {self.table_name}\n"
            " ALTER COLUMN user_id TYPE BIGINT USING user_id::BIGINT,\n"
            " ALTER COLUMN server_id TYPE BIGINT USING server_id::BIGINT,\n"
            " ALTER COLUMN channel_id TYPE BIGINT USING channel_id::BIGINT\n"
        )

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute((
            f"CREATE TABLE {self.table_name} ("
            " id SERIAL PRIMARY KEY,\n"
            " user_id VARCHAR(20) NOT NULL,"
            " server_id VARCHAR(20) NOT NULL,"
            " channel_id VARCHAR(20) NOT NULL,"
            " base_time TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),"
            " countdown_interval INTERVAL NOT NULL,"
            " name_template VARCHAR(20) DEFAULT NULL,"
            " expiry_name_template VARCHAR(20) DEFAULT NULL"
            ")"
        ))
