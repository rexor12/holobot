from asyncpg.connection import Connection

from holobot.sdk.database.migration import MigrationBase, MigrationInterface
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

_TABLE_NAME = "external_giveaway_items"

@injectable(MigrationInterface)
class ExternalGiveawayItemMigration(MigrationBase):
    def __init__(self) -> None:
        super().__init__(_TABLE_NAME, {
            0: MigrationPlan(0, 1, self.__initialize_table),
            1: MigrationPlan(1, 2, self.__upgrade_to_v2)
        }, {})

    async def __upgrade_to_v2(self, connection: Connection) -> None:
        await connection.execute((
            f"ALTER TABLE {_TABLE_NAME}"
            " ALTER COLUMN url TYPE VARCHAR(1024),"
            " ALTER COLUMN preview_url TYPE VARCHAR(1024),"
            " ALTER COLUMN title TYPE VARCHAR(512)"
        ))

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute(f"DROP TABLE IF EXISTS {_TABLE_NAME}")
        await connection.execute((
            f"CREATE TABLE {_TABLE_NAME} ("
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
