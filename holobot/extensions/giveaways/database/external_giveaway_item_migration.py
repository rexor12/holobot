from asyncpg.connection import Connection
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.database.migration import MigrationBase, MigrationInterface
from holobot.sdk.database.migration.models import MigrationPlan

TABLE_NAME = "external_giveaway_items"

@injectable(MigrationInterface)
class ExternalGiveawayItemMigration(MigrationBase):
    def __init__(self) -> None:
        super().__init__(TABLE_NAME, {
            0: MigrationPlan(0, 1, self.__initialize_table)
        }, {})

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
        await connection.execute((
            f"CREATE TABLE {TABLE_NAME} ("
            " id SERIAL PRIMARY KEY,"
            " created_at TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),"
            " start_time TIMESTAMP DEFAULT NULL,"
            " end_time TIMESTAMP NOT NULL,"
            " source_name VARCHAR(32) NOT NULL,"
            " item_type VARCHAR(32) NOT NULL,"
            " url VARCHAR(168) NOT NULL,"
            " preview_url VARCHAR(168) DEFAULT NULL,"
            " title VARCHAR(168) NOT NULL"
            ")"
        ))
