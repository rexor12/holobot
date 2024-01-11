from asyncpg.connection import Connection

from holobot.sdk.database.migration import MigrationBase, MigrationInterface
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(MigrationInterface)
class ChannelTimerMigration(MigrationBase):
    _TABLE_NAME = "channel_timers"

    def __init__(self) -> None:
        super().__init__(ChannelTimerMigration._TABLE_NAME, {
            0: MigrationPlan(0, 1, self.__initialize_table)
        }, {})

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute((
            f"CREATE TABLE {ChannelTimerMigration._TABLE_NAME} ("
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
