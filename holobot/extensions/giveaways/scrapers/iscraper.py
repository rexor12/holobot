from ..models import ExternalGiveawayItem
from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import Optional, Sequence

class IScraper(metaclass=ABCMeta):
    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def get_next_scrape_time(self, last_scrape_time: Optional[datetime]) -> datetime:
        ...

    @abstractmethod
    async def scrape(self) -> Sequence[ExternalGiveawayItem]:
        ...
