from asyncpg.connection import Connection

from holobot.sdk.database.migration import IMigration, MigrationBase
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(IMigration)
class ScraperInfoMigration(MigrationBase):
    def __init__(self) -> None:
        super().__init__(
            "scraper_infos",
            [
                MigrationPlan(1, self.__initialize_table)
            ]
        )

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute(f"DROP TABLE IF EXISTS {self.table_name}")
        await connection.execute((
            f"CREATE TABLE {self.table_name} ("
            " id SERIAL PRIMARY KEY,"
            " scraper_name VARCHAR(168) NOT NULL,"
            " last_scrape_time TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc')"
            ")"
        ))
