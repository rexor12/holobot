from dataclasses import dataclass
from datetime import datetime

@dataclass
class ScraperInfo:
    identifier: int
    scraper_name: str
    last_scrape_time: datetime
