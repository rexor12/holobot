from dataclasses import dataclass
from datetime import datetime

from holobot.sdk.database import AggregateRoot

@dataclass(kw_only=True)
class ScraperInfo(AggregateRoot[int]):
    identifier: int = -1
    scraper_name: str
    last_scrape_time: datetime
