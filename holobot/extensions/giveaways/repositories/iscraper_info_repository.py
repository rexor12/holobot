from ..models import ScraperInfo
from abc import ABCMeta, abstractmethod
from typing import Optional

class IScraperInfoRepository(metaclass=ABCMeta):
    @abstractmethod
    async def get(self, item_id: int) -> Optional[ScraperInfo]:
        ...

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[ScraperInfo]:
        ...

    @abstractmethod
    async def store(self, item: ScraperInfo) -> None:
        ...

    @abstractmethod
    async def delete(self, item_id: int) -> None:
        ...
