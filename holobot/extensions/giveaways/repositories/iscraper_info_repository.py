from typing import Protocol

from holobot.extensions.giveaways.models import ScraperInfo

class IScraperInfoRepository(Protocol):
    async def get(self, item_id: int) -> ScraperInfo | None:
        ...

    async def get_by_name(self, name: str) -> ScraperInfo | None:
        ...

    async def store(self, item: ScraperInfo) -> None:
        ...

    async def delete(self, item_id: int) -> None:
        ...
