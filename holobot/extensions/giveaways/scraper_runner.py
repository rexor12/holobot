from .models import ScraperInfo
from .repositories import IExternalGiveawayItemRepository, IScraperInfoRepository
from .scrapers import IScraper
from datetime import datetime, timezone
from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.lifecycle import IStartable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.threading import CancellationToken, CancellationTokenSource
from holobot.sdk.threading.utils import wait
from typing import Awaitable, Optional, Tuple

import asyncio
import contextlib

DEFAULT_RESOLUTION: int = 60
DEFAULT_DELAY: int = 40

@injectable(IStartable)
class ScraperRunner(IStartable):
    def __init__(self,
        configurator: ConfiguratorInterface,
        external_giveaway_item_repository: IExternalGiveawayItemRepository,
        logger_factory: ILoggerFactory,
        scraper_info_repository: IScraperInfoRepository,
        scrapers: Tuple[IScraper, ...]) -> None:
        super().__init__()
        self.__configurator: ConfiguratorInterface = configurator
        self.__external_giveaway_item_repository: IExternalGiveawayItemRepository = external_giveaway_item_repository
        self.__logger = logger_factory.create(ScraperRunner)
        self.__scraper_info_repository: IScraperInfoRepository = scraper_info_repository
        self.__scrapers: Tuple[IScraper, ...] = scrapers
        self.__process_resolution = self.__configurator.get("Giveaways", "RunnerResolution", DEFAULT_RESOLUTION)
        self.__process_delay = self.__configurator.get("Giveaways", "RunnerDelay", DEFAULT_DELAY)
        self.__token_source: Optional[CancellationTokenSource] = None
        self.__background_task: Optional[Awaitable[None]] = None

    async def start(self) -> None:
        if not self.__configurator.get("Giveaways", "EnableScrapers", True):
            self.__logger.info("Giveaway scraping is disabled by configuration.")
            return

        if len(self.__scrapers) == 0:
            self.__logger.info("Giveaway scraping is disabled, because there are no loaded scrapers.")
            return

        self.__logger.info(f"Giveaway scraping is enabled. {{ Delay = {self.__process_delay}, Resolution = {self.__process_resolution} }}")
        self.__token_source = CancellationTokenSource()
        self.__background_task = asyncio.create_task(
            self.__run_scrapers(self.__token_source.token)
        )

    async def stop(self) -> None:
        if self.__token_source:
            self.__token_source.cancel()
        if self.__background_task:
            with contextlib.suppress(asyncio.exceptions.CancelledError):
                await self.__background_task
        self.__logger.debug("Stopped background task.")

    async def __run_scrapers(self, token: CancellationToken):
        await wait(self.__process_delay, token)
        while not token.is_cancellation_requested:
            self.__logger.trace("Running giveaway scrapers...")
            try:
                for scraper in self.__scrapers:
                    await self.__run_scraper(scraper)
            finally:
                self.__logger.trace("Ran giveaway scrapers.")
            await wait(self.__process_resolution, token)

    async def __run_scraper(self, scraper: IScraper) -> None:
        try:
            scraper_name = type(scraper).__name__
            scraper_info = await self.__scraper_info_repository.get_by_name(scraper_name)
            last_scrape_time = scraper_info.last_scrape_time if scraper_info else None

            next_scrape_time = scraper.get_next_scrape_time(last_scrape_time)
            if datetime.now(timezone.utc) < next_scrape_time:
                return

            self.__logger.trace(f"Running giveaway scraper... {{ Name = {scraper_name} }}")
            giveaway_items = await scraper.scrape()
            self.__logger.trace(f"Ran giveaway scraper. {{ Name = {scraper_name} }}")
            for item in giveaway_items:
                if not await self.__external_giveaway_item_repository.exists(item.url):
                    await self.__external_giveaway_item_repository.store(item)

            if scraper_info:
                scraper_info.last_scrape_time = datetime.now(timezone.utc)
            else: scraper_info = ScraperInfo(0, scraper_name, datetime.now(timezone.utc))

            await self.__scraper_info_repository.store(scraper_info)
        except Exception as error: # pylint: disable=broad-except
            self.__logger.error("An error has occurred while running a giveaway scraper.", error)
