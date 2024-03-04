from dataclasses import dataclass
from datetime import datetime

from holobot.sdk.database.entities import PrimaryKey, Record

@dataclass
class ScraperInfoRecord(Record):
    id: PrimaryKey[int]
    scraper_name: str
    last_scrape_time: datetime
