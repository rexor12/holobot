from collections.abc import Sequence
from datetime import datetime
from typing import Protocol

from holobot.extensions.giveaways.models import ExternalGiveawayItem

class IScraper(Protocol):
    @property
    def name(self) -> str:
        ...

    def get_next_scrape_time(self, last_scrape_time: datetime | None) -> datetime:
        ...

    async def scrape(self) -> Sequence[ExternalGiveawayItem]:
        ...
