from asyncpg.connection import Connection

from holobot.extensions.giveaways.models import ScraperInfo
from holobot.sdk.database import DatabaseManagerInterface
from holobot.sdk.database.queries import Query
from holobot.sdk.database.queries.enums import Equality
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import set_time_zone, UTC
from .iscraper_info_repository import IScraperInfoRepository

_TABLE_NAME = "scraper_infos"

@injectable(IScraperInfoRepository)
class ScraperInfoRepository(IScraperInfoRepository):
    def __init__(self, database_manager: DatabaseManagerInterface) -> None:
        self.__database_manager: DatabaseManagerInterface = database_manager

    async def get(self, item_id: int) -> ScraperInfo | None:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                record = await (Query
                    .select()
                    .columns("id", "scraper_name", "last_scrape_time")
                    .from_table(_TABLE_NAME)
                    .where()
                    .field("id", Equality.EQUAL, item_id)
                    .compile()
                    .fetchrow(connection)
                )
                return ScraperInfoRepository.__parse_record(record) if record else None

    async def get_by_name(self, name: str) -> ScraperInfo | None:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                record = await (Query
                    .select()
                    .columns("id", "scraper_name", "last_scrape_time")
                    .from_table(_TABLE_NAME)
                    .where()
                    .field("scraper_name", Equality.EQUAL, name)
                    .compile()
                    .fetchrow(connection)
                )
                return ScraperInfoRepository.__parse_record(record) if record else None

    async def store(self, item: ScraperInfo) -> None:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                await (Query
                    .insert()
                    .in_table(_TABLE_NAME)
                    .fields(
                        ("id", item.identifier),
                        ("scraper_name", item.scraper_name),
                        ("last_scrape_time", set_time_zone(item.last_scrape_time, None))
                    )
                    .on_conflict("id")
                    .update()
                    .field("last_scrape_time", set_time_zone(item.last_scrape_time, None))
                    .compile()
                    .execute(connection)
                )

    async def delete(self, item_id: int) -> None:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                await Query.delete().from_table(_TABLE_NAME).where().field(
                    "id", Equality.EQUAL, item_id
                ).compile().execute(connection)

    @staticmethod
    def __parse_record(record) -> ScraperInfo:
        return ScraperInfo(
            record["id"],
            record["scraper_name"],
            set_time_zone(record["last_scrape_time"], UTC)
        )
