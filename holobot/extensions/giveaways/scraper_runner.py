import asyncio
import contextlib
from collections.abc import Awaitable

from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.lifecycle import IStartable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.network.resilience.exceptions import CircuitBrokenError
from holobot.sdk.reactive import IListener
from holobot.sdk.threading import CancellationToken, CancellationTokenSource
from holobot.sdk.threading.utils import wait
from holobot.sdk.utils import utcnow
from .events.models import NewGiveawaysEvent
from .models import ExternalGiveawayItem, ScraperInfo
from .repositories import IExternalGiveawayItemRepository, IScraperInfoRepository
from .scrapers import IScraper

DEFAULT_RESOLUTION: int = 60
DEFAULT_DELAY: int = 40

@injectable(IStartable)
class ScraperRunner(IStartable):
    def __init__(
        self,
        configurator: ConfiguratorInterface,
        external_giveaway_item_repository: IExternalGiveawayItemRepository,
        listeners: tuple[IListener[NewGiveawaysEvent], ...],
        logger_factory: ILoggerFactory,
        scraper_info_repository: IScraperInfoRepository,
        scrapers: tuple[IScraper, ...]
    ) -> None:
        super().__init__()
        self.__configurator = configurator
        self.__external_giveaway_item_repository = external_giveaway_item_repository
        self.__listeners = listeners
        self.__logger = logger_factory.create(ScraperRunner)
        self.__scraper_info_repository = scraper_info_repository
        self.__scrapers = scrapers
        self.__process_resolution = self.__configurator.get("Giveaways", "RunnerResolution", DEFAULT_RESOLUTION)
        self.__process_delay = self.__configurator.get("Giveaways", "RunnerDelay", DEFAULT_DELAY)
        self.__token_source: CancellationTokenSource | None = None
        self.__background_task: Awaitable[None] | None = None

    async def start(self) -> None:
        if not self.__configurator.get("Giveaways", "EnableScrapers", True):
            self.__logger.info("Giveaway scraping is disabled by configuration")
            return

        if not self.__scrapers:
            self.__logger.info("Giveaway scraping is disabled, because there are no loaded scrapers")
            return

        self.__logger.info("Giveaway scraping is enabled", delay=self.__process_delay, resolution=self.__process_resolution)
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
        self.__logger.debug("Stopped background task")

    async def __run_scrapers(self, token: CancellationToken):
        await wait(self.__process_delay, token)
        while not token.is_cancellation_requested:
            self.__logger.trace("Running giveaway scrapers...")
            run_count = 0
            giveaway_items: list[ExternalGiveawayItem] = []
            for scraper in self.__scrapers:
                giveaway_items.extend(await self.__run_scraper(scraper))
                run_count += 1
            self.__logger.trace("Ran giveaway scrapers", count=run_count)

            await self.__notify_listeners(tuple(giveaway_items))

            deleted_count = await self.__external_giveaway_item_repository.delete_expired()
            if deleted_count > 0:
                self.__logger.debug("Deleted expired giveaway items", count=deleted_count)

            await wait(self.__process_resolution, token)

    async def __run_scraper(self, scraper: IScraper) -> tuple[ExternalGiveawayItem, ...]:
        try:
            scraper_name = type(scraper).__name__
            scraper_info = await self.__scraper_info_repository.get_by_name(scraper_name)
            last_scrape_time = scraper_info.last_scrape_time if scraper_info else None

            next_scrape_time = scraper.get_next_scrape_time(last_scrape_time)
            if utcnow() < next_scrape_time:
                self.__logger.trace("Postponed scraping", name=scraper_name, scrape_at=next_scrape_time)
                return ()

            self.__logger.trace("Running giveaway scraper...", name=scraper_name)
            scraped_giveaway_items = await scraper.scrape()
            new_giveaway_items: list[ExternalGiveawayItem] = []
            self.__logger.trace("Ran giveaway scraper", name=scraper_name)
            for item in scraped_giveaway_items:
                if not await self.__external_giveaway_item_repository.exists(item.url):
                    new_giveaway_items.append(item)
                    await self.__external_giveaway_item_repository.add(item)

            if scraper_info:
                scraper_info.last_scrape_time = utcnow()
                await self.__scraper_info_repository.update(scraper_info)
            else:
                await self.__scraper_info_repository.add(
                ScraperInfo(scraper_name=scraper_name, last_scrape_time=utcnow())
            )

            return tuple(new_giveaway_items)
        except CircuitBrokenError:
            return ()
        except Exception as error: # pylint: disable=broad-except
            self.__logger.error("An error has occurred while running a giveaway scraper", error)
            return ()

    async def __notify_listeners(
        self,
        giveaway_items: tuple[ExternalGiveawayItem, ...]
    ) -> None:
        if not giveaway_items:
            return

        event = NewGiveawaysEvent(giveaways=giveaway_items)
        for listener in self.__listeners:
            try:
                await listener.on_event(event)
            except Exception as error:
                self.__logger.error("Failed to execute listener", error, listener_type=type(listener).__name__)
