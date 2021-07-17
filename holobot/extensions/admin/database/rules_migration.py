from asyncpg.connection import Connection
from holobot.sdk.database.migration import MigrationBase, MigrationInterface
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

TABLE_NAME = "admin_rules"

@injectable(MigrationInterface)
class RulesMigration(MigrationBase):
    def __init__(self):
        super().__init__(TABLE_NAME, {
            0: MigrationPlan(0, 1, self.__initialize_table)
        }, {})
    
    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
        await connection.execute((
            f"CREATE TABLE {TABLE_NAME} ("
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
