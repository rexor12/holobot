from asyncpg.connection import Connection

from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.database.migration import MigrationBase, MigrationInterface
from holobot.sdk.database.migration.models import MigrationPlan

_TABLE_NAME = "scraper_infos"

@injectable(MigrationInterface)
class ScraperInfoMigration(MigrationBase):
    def __init__(self) -> None:
        super().__init__(_TABLE_NAME, {
            0: MigrationPlan(0, 1, self.__initialize_table)
        }, {})

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute(f"DROP TABLE IF EXISTS {_TABLE_NAME}")
        await connection.execute((
            f"CREATE TABLE {_TABLE_NAME} ("
            " id SERIAL PRIMARY KEY,"
            " scraper_name VARCHAR(168) NOT NULL,"
            " last_scrape_time TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc')"
            ")"
        ))
