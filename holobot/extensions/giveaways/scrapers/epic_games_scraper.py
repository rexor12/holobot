import zoneinfo
from collections.abc import Sequence
from datetime import datetime, time, timedelta, timezone
from typing import Any

from holobot.extensions.giveaways.models import EpicScraperOptions, ExternalGiveawayItem
from holobot.sdk.configs import IOptions
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.network import IHttpClientPool
from holobot.sdk.network.exceptions import TooManyRequestsError
from holobot.sdk.network.resilience import AsyncCircuitBreakerPolicy
from holobot.sdk.serialization.json_serializer import deserialize
from holobot.sdk.utils import first_or_default, utcnow
from .dtos.epic_games_dtos import ChildPromotionalOffer, FreeGamesPromotions, Offer
from .iscraper import IScraper

SCRAPE_DELAY: timedelta = timedelta(minutes=5)
OFFER_IMAGE_TYPES: tuple[str, ...] = (
    "OfferImageWide", "DieselStoreFrontWide", "OfferImageTall", "Thumbnail"
)

# Epic Games always updates the free games on Thursdays at 10 PM CT.
EPIC_UPDATE_TIMEZONE = zoneinfo.ZoneInfo("US/Central")
EPIC_UPDATE_DAYOFWEEK = 3
EPIC_UPDATE_TIME = time(hour=10)

@injectable(IScraper)
class EpicGamesScraper(IScraper):
    def __init__(
        self,
        http_client_pool: IHttpClientPool,
        logger_factory: ILoggerFactory,
        options: IOptions[EpicScraperOptions]
    ) -> None:
        super().__init__()
        self.__logger = logger_factory.create(EpicGamesScraper)
        self.__http_client_pool = http_client_pool
        self.__options = options
        self.__circuit_breaker = EpicGamesScraper.__create_circuit_breaker(options.value)

    @property
    def name(self) -> str:
        return "Epic Games Store"

    def get_next_scrape_time(self, last_scrape_time: datetime | None) -> datetime:
        if last_scrape_time is None:
            return utcnow() - timedelta(minutes=1)

        today = datetime.now(EPIC_UPDATE_TIMEZONE).date()
        time_to_nearest_release_day = timedelta(days=EPIC_UPDATE_DAYOFWEEK - today.weekday())
        if today.weekday() >= EPIC_UPDATE_DAYOFWEEK:
            previous_thursday = today - timedelta(days=today.weekday() - EPIC_UPDATE_DAYOFWEEK)
            next_thursday = today + timedelta(weeks=1) + time_to_nearest_release_day
        else:
            previous_thursday = today - timedelta(weeks=1) + time_to_nearest_release_day
            next_thursday = today + time_to_nearest_release_day
        previous_release_time = datetime.combine(previous_thursday, EPIC_UPDATE_TIME, EPIC_UPDATE_TIMEZONE)
        if last_scrape_time < previous_release_time:
            if utcnow() > previous_release_time:
                return utcnow() - timedelta(minutes=1)
            else:
                return previous_release_time.astimezone(timezone.utc)

        next_release_time = datetime.combine(next_thursday, EPIC_UPDATE_TIME, EPIC_UPDATE_TIMEZONE)
        return next_release_time.astimezone(timezone.utc) + SCRAPE_DELAY

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
            giveaway_time = EpicGamesScraper.__get_giveaway_data(item)
            if not giveaway_time:
                self.__logger.debug("Ignored item, because it has no active offer", title=item.title)
                continue

            product_slug = first_or_default(item.catalogNs.mappings, lambda i: i.pageType == "productHome")
            page_slug = product_slug.pageSlug if product_slug else item.productSlug
            if not page_slug:
                self.__logger.debug("Ignored item, because it has no product slug", title=item.title)
                continue

            giveaway_items.append(ExternalGiveawayItem(
                0,
                utcnow(),
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
        now = utcnow()
        return ((offer.startDate is None or offer.startDate <= now)
                and (offer.endDate is None or offer.endDate > now)
                and offer.discountSetting.discountType is not None
                and offer.discountSetting.discountPercentage is not None
                and offer.discountSetting.discountType.upper() == "PERCENTAGE"
                and not int(offer.discountSetting.discountPercentage))

    @staticmethod
    def __get_preview_image(offer: Offer) -> str | None:
        for image_key in OFFER_IMAGE_TYPES:
            if image := first_or_default(offer.keyImages, lambda i, k=image_key: i.type == k, None):
                return image.url
        return None
