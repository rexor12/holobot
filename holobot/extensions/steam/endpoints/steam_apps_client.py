from typing import Any

from holobot.extensions.steam.models import SteamApp, SteamAppsOptions
from holobot.sdk.configs import IOptions
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.network import IHttpClientPool
from holobot.sdk.network.exceptions import HttpStatusError, TooManyRequestsError
from holobot.sdk.network.resilience import AsyncCircuitBreakerPolicy
from holobot.sdk.network.resilience.exceptions import CircuitBrokenError
from holobot.sdk.serialization.json_serializer import deserialize
from holobot.sdk.utils.http_utils import build_url
from .dtos.get_app_list_response import GetAppListResponse
from .isteam_apps_client import ISteamAppsClient

@injectable(ISteamAppsClient)
class SteamAppsClient(ISteamAppsClient):
    def __init__(
        self,
        http_client_pool: IHttpClientPool,
        logger_factory: ILoggerFactory,
        options: IOptions[SteamAppsOptions]
    ) -> None:
        super().__init__()
        self.__http_client_pool = http_client_pool
        self.__log = logger_factory.create(SteamAppsClient)
        self.__get_app_list_api_url = build_url(
            options.value.BaseUrl,
            ("GetAppList", "v2")
        )
        self.__circuit_breaker = AsyncCircuitBreakerPolicy[str, Any](
            options.value.CircuitBreakerFailureThreshold,
            options.value.CircuitBreakerRecoveryTime,
            SteamAppsClient.__on_circuit_broken
        )

    async def get_app_list(self) -> tuple[SteamApp, ...]:
        try:
            response = await self.__circuit_breaker(
                lambda s: self.__http_client_pool.get(s),
                self.__get_app_list_api_url
            )
        # TODO Don't forget to handle TooManyRequestsError outside.
        # except TooManyRequestsError as error:
        #     raise QuotaExhaustedError from error
        except HttpStatusError as error:
            self.__log.error("An HTTP error has occurred during a SteamApps->GetAppList request", error)
            raise
        except CircuitBrokenError:
            raise
        except Exception as error:
            self.__log.error("An unexpected error has occurred during a SteamApps->GetAppList request", error)
            raise

        response_dto = deserialize(GetAppListResponse, response)
        if not response_dto:
            return ()

        return tuple(
            SteamApp(
                identifier=item.appid,
                name=item.name
            )
            for item in response_dto.applist.apps
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
