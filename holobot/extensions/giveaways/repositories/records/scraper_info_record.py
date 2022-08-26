from dataclasses import dataclass
from datetime import datetime

from holobot.sdk.database.repositories import Entity

@dataclass
class ScraperInfoRecord(Entity[int]):
    id: int
    scraper_name: str
    last_scrape_time: datetime
