from holobot.extensions.giveaways.models import ScraperInfo
from holobot.sdk.database import IDatabaseManager, IUnitOfWorkProvider
from holobot.sdk.database.queries.enums import Equality
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.ioc.decorators import injectable
from .iscraper_info_repository import IScraperInfoRepository
from .records import ScraperInfoRecord

@injectable(IScraperInfoRepository)
class ScraperInfoRepository(
    RepositoryBase[int, ScraperInfoRecord, ScraperInfo],
    IScraperInfoRepository
):
    @property
    def record_type(self) -> type[ScraperInfoRecord]:
        return ScraperInfoRecord

    @property
    def model_type(self) -> type[ScraperInfo]:
        return ScraperInfo

    @property
    def table_name(self) -> str:
        return "scraper_infos"

    def __init__(
        self,
        database_manager: IDatabaseManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__(database_manager, unit_of_work_provider)

    async def get_by_name(self, name: str) -> ScraperInfo | None:
        return await self._get_by_filter(lambda where: (
            where.field("scraper_name", Equality.EQUAL, name)
        ))

    def _map_record_to_model(self, record: ScraperInfoRecord) -> ScraperInfo:
        return ScraperInfo(
            identifier=record.id,
            scraper_name=record.scraper_name,
            last_scrape_time=record.last_scrape_time
        )

    def _map_model_to_record(self, model: ScraperInfo) -> ScraperInfoRecord:
        return ScraperInfoRecord(
            id=model.identifier,
            scraper_name=model.scraper_name,
            last_scrape_time=model.last_scrape_time
        )
