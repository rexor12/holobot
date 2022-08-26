from dataclasses import dataclass
from datetime import datetime

@dataclass(kw_only=True)
class ScraperInfo:
    identifier: int = -1
    scraper_name: str
    last_scrape_time: datetime
