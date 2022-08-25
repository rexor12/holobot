from typing import Protocol

from holobot.extensions.giveaways.models import ScraperInfo
from holobot.sdk.database.repositories import IRepository

class IScraperInfoRepository(IRepository[int, ScraperInfo], Protocol):
    async def get_by_name(self, name: str) -> ScraperInfo | None:
        ...
