import zoneinfo
from collections.abc import Sequence
from datetime import datetime, time, timedelta, timezone
from typing import Any

from holobot.extensions.giveaways.models import EpicScraperOptions, ExternalGiveawayItem
from holobot.sdk.chrono import IClock
from holobot.sdk.configs import IOptions
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.network import IHttpClientPool
from holobot.sdk.network.exceptions import TooManyRequestsError
from holobot.sdk.network.resilience import AsyncCircuitBreakerPolicy
from holobot.sdk.serialization.json_serializer import deserialize
from holobot.sdk.utils import first_or_default
from .dtos.epic_games_dtos import ChildPromotionalOffer, FreeGamesPromotions, Offer
from .iscraper import IScraper

OFFER_IMAGE_TYPES: tuple[str, ...] = (
    "OfferImageWide", "DieselStoreFrontWide", "OfferImageTall", "Thumbnail"
)

# Epic Games always updates the free games on Thursdays at 10 PM CT.
# But we'll check daily for random promotions.
EPIC_UPDATE_TIMEZONE = zoneinfo.ZoneInfo("US/Central")
EPIC_UPDATE_TIME = time(hour=10)
EXECUTION_DELAY = timedelta(seconds=5 * 60)

@injectable(IScraper)
class EpicGamesScraper(IScraper):
    def __init__(
        self,
        clock: IClock,
        http_client_pool: IHttpClientPool,
        logger_factory: ILoggerFactory,
        options: IOptions[EpicScraperOptions]
    ) -> None:
        super().__init__()
        self.__clock = clock
        self.__logger = logger_factory.create(EpicGamesScraper)
        self.__http_client_pool = http_client_pool
        self.__options = options
        self.__circuit_breaker = EpicGamesScraper.__create_circuit_breaker(options.value)

    @property
    def name(self) -> str:
        return "Epic Games Store"

    def get_next_scrape_time(self, last_scrape_time: datetime | None) -> datetime:
        now = self.__clock.now_utc()
        if last_scrape_time is None:
            return now - timedelta(minutes=1)

        today = now.astimezone(EPIC_UPDATE_TIMEZONE).date()
        release_time_today = datetime.combine(today, EPIC_UPDATE_TIME, EPIC_UPDATE_TIMEZONE) + EXECUTION_DELAY
        if last_scrape_time < release_time_today:
            if now > release_time_today:
                return now - timedelta(minutes=1)
            return release_time_today.astimezone(timezone.utc)

        release_time_tomorrow = datetime.combine(today + timedelta(days=1), EPIC_UPDATE_TIME, EPIC_UPDATE_TIMEZONE) + EXECUTION_DELAY
        return release_time_tomorrow.astimezone(timezone.utc)

    async def scrape(self) -> Sequence[ExternalGiveawayItem]:
        options = self.__options.value
        response = await self.__circuit_breaker(
            lambda s: self.__http_client_pool.get(s[0], s[1]),
            (
                options.Url,
                { "country": options.CountryCode }
            )
        )

        promotions = deserialize(FreeGamesPromotions, response)
        if not promotions or not promotions.data.Catalog.searchStore.elements:
            return ()

        giveaway_items = []
        for item in promotions.data.Catalog.searchStore.elements:
            giveaway_time = self.__get_giveaway_data(item)
            if not giveaway_time:
                self.__logger.debug("Ignored item, because it has no active offer", title=item.title)
                continue

            if not (page_slug := EpicGamesScraper.__get_page_slug(item)):
                self.__logger.debug("Ignored item, because it has no product slug", title=item.title)
                continue

            giveaway_items.append(ExternalGiveawayItem(
                0,
                self.__clock.now_utc(),
                giveaway_time.startDate.astimezone(timezone.utc) if giveaway_time.startDate else None,
                giveaway_time.endDate.astimezone(timezone.utc) if giveaway_time.endDate else datetime.max.astimezone(timezone.utc),
                self.name,
                "game",
                f"https://store.epicgames.com/en-US/p/{page_slug}",
                EpicGamesScraper.__get_preview_image(item),
                item.title or "Unknown game"
            ))

        return giveaway_items

    @staticmethod
    def __create_circuit_breaker(
        options: EpicScraperOptions
    ) -> AsyncCircuitBreakerPolicy[tuple[str, dict[str, Any]], Any]:
        return AsyncCircuitBreakerPolicy[tuple[str, dict[str, Any]], Any](
            options.CircuitBreakerFailureThreshold,
            options.CircuitBreakerRecoveryTime,
            EpicGamesScraper.__on_circuit_broken
        )

    @staticmethod
    async def __on_circuit_broken(
        circuit_breaker: AsyncCircuitBreakerPolicy[tuple[str, dict[str, Any]], Any],
        error: Exception
    ) -> int:
        if (isinstance(error, TooManyRequestsError)
            and error.retry_after is not None
            and isinstance(error.retry_after, int)):
            return error.retry_after
        return circuit_breaker.recovery_timeout

    @staticmethod
    def __get_preview_image(offer: Offer) -> str | None:
        for image_key in OFFER_IMAGE_TYPES:
            if image := first_or_default(offer.keyImages, lambda i, k=image_key: i.type == k, None):
                return image.url
        return None

    @staticmethod
    def __get_page_slug(offer: Offer) -> str | None:
        if offer.productSlug:
            return offer.productSlug

        custom_attribute = first_or_default(
            offer.customAttributes,
            lambda i: i.key == "com.epicgames.app.productSlug"
        )
        if custom_attribute and custom_attribute.value:
            return custom_attribute.value

        product_home = first_or_default(
            offer.catalogNs.mappings,
            lambda i: i.pageType == "productHome"
        )

        return product_home.pageSlug if product_home else None

    def __get_giveaway_data(self, item: Offer) -> ChildPromotionalOffer | None:
        offers: list[ChildPromotionalOffer] = []
        for promotional_offer in item.promotions.promotionalOffers:
            offers.extend(
                child_promotional_offer
                for child_promotional_offer in promotional_offer.promotionalOffers
                if self.__is_active_giveaway(child_promotional_offer)
            )

        if not offers:
            return None

        sorted_offers = sorted(
            offers,
            key=lambda i: i.endDate or datetime.min.astimezone(timezone.utc),
            reverse=True
        )
        return sorted_offers[0]

    def __is_active_giveaway(self, offer: ChildPromotionalOffer) -> bool:
        now = self.__clock.now_utc()
        return ((offer.startDate is None or offer.startDate <= now)
                and (offer.endDate is None or offer.endDate > now)
                and offer.discountSetting.discountType is not None
                and offer.discountSetting.discountPercentage is not None
                and offer.discountSetting.discountType.upper() == "PERCENTAGE"
                and not int(offer.discountSetting.discountPercentage))
