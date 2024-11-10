from asyncpg.connection import Connection

from holobot.sdk.database.migration import IMigration, MigrationBase
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(IMigration)
class MutesMigration(MigrationBase):
    def __init__(self):
        super().__init__(
            "moderation_mutes",
            [
                MigrationPlan(1, self.__initialize_table),
                MigrationPlan(2, self.__upgrade_to_v2)
            ]
        )

    async def __upgrade_to_v2(self, connection: Connection) -> None:
        await connection.execute(f"DROP TABLE {self.table_name}")

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute(f"DROP TABLE IF EXISTS {self.table_name}")
        await connection.execute((
            f"CREATE TABLE {self.table_name} ("
            " id SERIAL PRIMARY KEY,"
            " modified_at TIMESTAMP DEFAULT (NOW() at time zone 'utc'),"
            " server_id VARCHAR(20) NOT NULL,"
            " user_id VARCHAR(20) NOT NULL,"
            " expires_at TIMESTAMP NOT NULL,"
            " UNIQUE(server_id, user_id)"
            " )"
        ))
