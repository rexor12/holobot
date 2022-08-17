import zoneinfo
from collections.abc import Sequence
from datetime import datetime, time, timedelta, timezone

from holobot.extensions.giveaways.models import ExternalGiveawayItem
from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.network import HttpClientPoolInterface
from holobot.sdk.network.exceptions import TooManyRequestsError
from holobot.sdk.network.resilience import AsyncCircuitBreaker
from holobot.sdk.serialization.json_serializer import deserialize
from holobot.sdk.utils import first_or_default
from .dtos.epic_games_dtos import ChildPromotionalOffer, FreeGamesPromotions, Offer
from .iscraper import IScraper

CONFIG_SECTION = "Giveaways"
CIRCUIT_BREAKER_FAILURE_THRESHOLD_PARAMETER = "EpicScraperCircuitBreakerFailureThreshold"
CIRCUIT_BREAKER_RECOVERY_TIME_PARAMETER = "EpicScraperCircuitBreakerRecoveryTime"
URL_PARAMETER = "EpicScraperUrl"
COUNTRY_CODE_PARAMETER = "EpicScraperCountryCode"
SCRAPE_DELAY: timedelta = timedelta(minutes=5)
OFFER_IMAGE_TYPES: tuple[str, ...] = (
    "OfferImageWide", "DieselStoreFrontWide", "OfferImageTall", "Thumbnail"
)

# Epic Games always updates the free games on Thursdays at 10 PM CT.
EPIC_UPDATE_TIMEZONE = zoneinfo.ZoneInfo("US/Central")
EPIC_UPDATE_TIME = time(hour=10)

@injectable(IScraper)
class EpicGamesScraper(IScraper):
    def __init__(
        self,
        configurator: ConfiguratorInterface,
        http_client_pool: HttpClientPoolInterface,
        logger_factory: ILoggerFactory
    ) -> None:
        super().__init__()
        self.__logger = logger_factory.create(EpicGamesScraper)
        self.__http_client_pool = http_client_pool
        self.__url = configurator.get(CONFIG_SECTION, URL_PARAMETER, "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions")
        self.__country_code = configurator.get(CONFIG_SECTION, COUNTRY_CODE_PARAMETER, "US")
        self.__circuit_breaker = EpicGamesScraper.__create_circuit_breaker(configurator)

    @property
    def name(self) -> str:
        return "Epic Games Store"

    def get_next_scrape_time(self, last_scrape_time: datetime | None) -> datetime:
        if last_scrape_time is None:
            return datetime.now(timezone.utc) - timedelta(minutes=1)

        today = datetime.now(EPIC_UPDATE_TIMEZONE).date()
        previous_thursday = today - timedelta(days=abs(3 - today.weekday()))
        previous_release_time = datetime.combine(previous_thursday, EPIC_UPDATE_TIME, EPIC_UPDATE_TIMEZONE)
        if last_scrape_time < previous_release_time:
            return datetime.now(timezone.utc) - timedelta(minutes=1)

        next_thursday = today + timedelta(days=3 - today.weekday(), weeks=1)
        next_release_time = datetime.combine(next_thursday, EPIC_UPDATE_TIME, EPIC_UPDATE_TIMEZONE)
        return next_release_time.astimezone(timezone.utc) + SCRAPE_DELAY

    async def scrape(self) -> Sequence[ExternalGiveawayItem]:
        response = await self.__circuit_breaker(
            self.__http_client_pool.get,
            self.__url,
            {
                "country": self.__country_code
            })

        promotions = deserialize(FreeGamesPromotions, response)
        if not promotions or not promotions.data.Catalog.searchStore.elements:
            return ()

        giveaway_items = []
        for item in promotions.data.Catalog.searchStore.elements:
            giveaway_time = EpicGamesScraper.__get_giveaway_data(item)
            if not giveaway_time:
                self.__logger.debug("Ignored item, because it has no active offer", title=item.title)
                continue

            product_slug = first_or_default(item.catalogNs.mappings, lambda i: i.pageType == "productHome")
            if not product_slug or not product_slug.pageSlug:
                self.__logger.debug("Ignored item, because it has no product slug", title=item.title)
                continue

            giveaway_items.append(ExternalGiveawayItem(
                0,
                datetime.now(timezone.utc),
                giveaway_time.startDate.astimezone(timezone.utc) if giveaway_time.startDate else None,
                giveaway_time.endDate.astimezone(timezone.utc) if giveaway_time.endDate else datetime.max.astimezone(timezone.utc),
                self.name,
                "game",
                f"https://store.epicgames.com/en-US/p/{product_slug.pageSlug}",
                EpicGamesScraper.__get_preview_image(item),
                item.title or "Unknown game"
            ))

        return giveaway_items

    @staticmethod
    def __create_circuit_breaker(
        configurator: ConfiguratorInterface
    ) -> AsyncCircuitBreaker:
        return AsyncCircuitBreaker(
            configurator.get(CONFIG_SECTION, CIRCUIT_BREAKER_FAILURE_THRESHOLD_PARAMETER, 1),
            configurator.get(CONFIG_SECTION, CIRCUIT_BREAKER_RECOVERY_TIME_PARAMETER, 300),
            EpicGamesScraper.__on_circuit_broken)

    @staticmethod
    async def __on_circuit_broken(
        circuit_breaker: AsyncCircuitBreaker,
        error: Exception
    ) -> int:
        if (isinstance(error, TooManyRequestsError)
            and error.retry_after is not None
            and isinstance(error.retry_after, int)):
            return error.retry_after
        return circuit_breaker.recovery_timeout

    @staticmethod
    def __get_giveaway_data(item: Offer) -> ChildPromotionalOffer | None:
        offers: list[ChildPromotionalOffer] = []
        for promotional_offer in item.promotions.promotionalOffers:
            offers.extend(
                child_promotional_offer
                for child_promotional_offer in promotional_offer.promotionalOffers
                if EpicGamesScraper.__is_active_giveaway(child_promotional_offer)
            )

        if not offers:
            return None

        sorted_offers = sorted(
            offers,
            key=lambda i: i.endDate or datetime.min.astimezone(timezone.utc),
            reverse=True
        )
        return sorted_offers[0]

    @staticmethod
    def __is_active_giveaway(offer: ChildPromotionalOffer) -> bool:
        now = datetime.now(timezone.utc)
        return ((offer.startDate is None or offer.startDate <= now)
                and (offer.endDate is None or offer.endDate > now)
                and offer.discountSetting.discountType is not None
                and offer.discountSetting.discountPercentage is not None
                and offer.discountSetting.discountType.upper() == "PERCENTAGE"
                and int(offer.discountSetting.discountPercentage) == 0)

    @staticmethod
    def __get_preview_image(offer: Offer) -> str | None:
        for image_key in OFFER_IMAGE_TYPES:
            if image := first_or_default(offer.keyImages, lambda i, k=image_key: i.type == k, None):
                return image.url
        return None
