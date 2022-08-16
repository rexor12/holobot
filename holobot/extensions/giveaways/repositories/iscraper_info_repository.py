from ..models import ScraperInfo
from typing import Optional, Protocol

class IScraperInfoRepository(Protocol):
    async def get(self, item_id: int) -> Optional[ScraperInfo]:
        ...

    async def get_by_name(self, name: str) -> Optional[ScraperInfo]:
        ...

    async def store(self, item: ScraperInfo) -> None:
        ...

    async def delete(self, item_id: int) -> None:
        ...
