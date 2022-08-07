from .iscraper import IScraper
from .dtos.epic_games_dtos import ChildPromotionalOffer, FreeGamesPromotions, Offer
from ..models import ExternalGiveawayItem
from datetime import datetime, time, timedelta, timezone
from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.network import HttpClientPoolInterface
from holobot.sdk.network.exceptions import TooManyRequestsError
from holobot.sdk.network.resilience import AsyncCircuitBreaker
from holobot.sdk.serialization.json_serializer import deserialize
from holobot.sdk.utils import first_or_default
from typing import List, Optional, Sequence

import zoneinfo

CONFIG_SECTION = "Giveaways"
CIRCUIT_BREAKER_FAILURE_THRESHOLD_PARAMETER = "EpicScraperCircuitBreakerFailureThreshold"
CIRCUIT_BREAKER_RECOVERY_TIME_PARAMETER = "EpicScraperCircuitBreakerRecoveryTime"
URL_PARAMETER = "EpicScraperUrl"
COUNTRY_CODE_PARAMETER = "EpicScraperCountryCode"
SCRAPE_DELAY: timedelta = timedelta(minutes=5)

@injectable(IScraper)
class EpicGamesScraper(IScraper):
    def __init__(
        self,
        configurator: ConfiguratorInterface,
        http_client_pool: HttpClientPoolInterface) -> None:
        super().__init__()
        self.__http_client_pool: HttpClientPoolInterface = http_client_pool
        self.__url: str = configurator.get(CONFIG_SECTION, URL_PARAMETER, "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions")
        self.__country_code: str = configurator.get(CONFIG_SECTION, COUNTRY_CODE_PARAMETER, "US")
        self.__circuit_breaker: AsyncCircuitBreaker = EpicGamesScraper.__create_circuit_breaker(configurator)

    @property
    def name(self) -> str:
        return "Epic Games Store"

    def get_next_scrape_time(self, last_scrape_time: Optional[datetime]) -> datetime:
        # Epic Games always updates the free games on Thursdays at 3 PM PT.
        pacific_time = zoneinfo.ZoneInfo("US/Pacific")
        if last_scrape_time is None:
            return datetime.now(timezone.utc) - timedelta(minutes=1)

        today = datetime.now(pacific_time).date()
        next_thursday = today + timedelta(days=3 - today.weekday(), weeks=1)
        next_release_time = datetime.combine(next_thursday, time(hour=15), pacific_time)
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
                continue

            product_slug = first_or_default(item.customAttributes, lambda i: i.key == "com.epicgames.app.productSlug", None)
            if not product_slug or not product_slug.value:
                continue

            preview_image = first_or_default(item.keyImages, lambda i: i.type == "DieselStoreFrontWide", None)
            giveaway_items.append(ExternalGiveawayItem(
                0,
                datetime.now(timezone.utc),
                giveaway_time.startDate.astimezone(timezone.utc) if giveaway_time.startDate else None,
                giveaway_time.endDate.astimezone(timezone.utc) if giveaway_time.endDate else datetime.max.astimezone(timezone.utc),
                self.name,
                "game",
                f"https://store.epicgames.com/en-US/p/{product_slug.value}",
                preview_image.url if preview_image else None,
                item.title or "Unknown game"
            ))

        return giveaway_items

    @staticmethod
    def __create_circuit_breaker(configurator: ConfiguratorInterface) -> AsyncCircuitBreaker:
        return AsyncCircuitBreaker(
            configurator.get(CONFIG_SECTION, CIRCUIT_BREAKER_FAILURE_THRESHOLD_PARAMETER, 1),
            configurator.get(CONFIG_SECTION, CIRCUIT_BREAKER_RECOVERY_TIME_PARAMETER, 300),
            EpicGamesScraper.__on_circuit_broken)

    @staticmethod
    async def __on_circuit_broken(circuit_breaker: AsyncCircuitBreaker, error: Exception) -> int:
        if (isinstance(error, TooManyRequestsError)
            and error.retry_after is not None
            and isinstance(error.retry_after, int)):
            return error.retry_after
        return circuit_breaker.recovery_timeout

    @staticmethod
    def __get_giveaway_data(item: Offer) -> Optional[ChildPromotionalOffer]:
        offers: List[ChildPromotionalOffer] = []
        for promotional_offer in item.promotions.promotionalOffers:
            offers.extend(
                child_promotional_offer for child_promotional_offer in promotional_offer.promotionalOffers
                if EpicGamesScraper.__is_active_giveaway(
                    child_promotional_offer.startDate,
                    child_promotional_offer.endDate,
                    child_promotional_offer.discountSetting.discountType,
                    int(child_promotional_offer.discountSetting.discountPercentage)
                )
            )

        if not offers:
            return None

        sorted_offers = sorted(offers, key=lambda i: i.endDate or datetime.min.astimezone(timezone.utc), reverse=True)
        return sorted_offers[0]

    @staticmethod
    def __is_active_giveaway(
        start_time: Optional[datetime],
        end_time: Optional[datetime],
        discount_type: Optional[str],
        discount_percentage: Optional[int]) -> bool:
        now = datetime.now(timezone.utc)
        return ((start_time is None or start_time <= now)
                and (end_time is None or end_time > now)
                and discount_type is not None
                and discount_percentage is not None
                and discount_type.upper() == "PERCENTAGE"
                and discount_percentage == 0)
