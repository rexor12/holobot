from typing import Protocol

class IScraperManager(Protocol):
    async def invalidate_scrape_time(self, scraper_name: str) -> None:
        ...
