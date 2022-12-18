from itertools import islice
from typing import Any

from holobot.extensions.steam.endpoints.dtos.search_apps_response import SearchAppsItem
from holobot.extensions.steam.models import SteamApp, SteamCommunityOptions
from holobot.sdk.configs import IOptions
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.network import IHttpClientPool
from holobot.sdk.network.exceptions import HttpStatusError, TooManyRequestsError
from holobot.sdk.network.resilience import AsyncCircuitBreakerPolicy
from holobot.sdk.network.resilience.exceptions import CircuitBrokenError
from holobot.sdk.serialization.json_serializer import deserialize
from holobot.sdk.utils.http_utils import build_url
from .isteam_community_client import ISteamCommunityClient

@injectable(ISteamCommunityClient)
class SteamCommunityClient(ISteamCommunityClient):
    def __init__(
        self,
        http_client_pool: IHttpClientPool,
        logger_factory: ILoggerFactory,
        options: IOptions[SteamCommunityOptions]
    ) -> None:
        super().__init__()
        self.__http_client_pool = http_client_pool
        self.__log = logger_factory.create(SteamCommunityClient)
        self.__options = options
        self.__circuit_breaker = AsyncCircuitBreakerPolicy[str, Any](
            options.value.CircuitBreakerFailureThreshold,
            options.value.CircuitBreakerRecoveryTime,
            SteamCommunityClient.__on_circuit_broken
        )

    async def search_apps(self, search_text: str) -> tuple[SteamApp, ...]:
        try:
            response = await self.__circuit_breaker.execute(
                lambda s: self.__http_client_pool.get(s),
                build_url(self.__options.value.BaseUrl, ("SearchApps", search_text))
            )
        except HttpStatusError as error:
            self.__log.error("An HTTP error has occurred during a SteamCommunity->SearchApps request", error)
            raise
        except CircuitBrokenError:
            raise
        except Exception as error:
            self.__log.error("An unexpected error has occurred during a SteamCommunity->SearchApps request", error)
            raise

        if not response or not isinstance(response, list):
            return ()

        response_apps = [deserialize(SearchAppsItem, item) for item in response]

        return tuple(
            SteamApp(
                identifier=item.appid,
                name=item.name,
                logo_url=item.logo
            )
            for item in islice(response_apps, self.__options.value.MaxSearchResults)
            if item
        )

    @staticmethod
    async def __on_circuit_broken(
        circuit_breaker: AsyncCircuitBreakerPolicy[tuple[str, dict[str, Any]], Any],
        error: Exception
    ) -> int:
        if (isinstance(error, TooManyRequestsError)
            and error.retry_after is not None
            and isinstance(error.retry_after, int)
        ):
            return error.retry_after
        return circuit_breaker.recovery_timeout
