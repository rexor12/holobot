from typing import Any

from holobot.extensions.steam.endpoints.dtos.get_app_details_response import AppDetails
from holobot.extensions.steam.models import SteamAppDetails, SteamAppDetailsOptions
from holobot.sdk.configs import IOptions
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.network import IHttpClientPool
from holobot.sdk.network.exceptions import HttpStatusError, TooManyRequestsError
from holobot.sdk.network.resilience import AsyncCircuitBreakerPolicy
from holobot.sdk.network.resilience.exceptions import CircuitBrokenError
from holobot.sdk.serialization.json_serializer import deserialize
from holobot.sdk.utils.http_utils import build_url
from .isteam_app_details_client import ISteamAppDetailsClient

@injectable(ISteamAppDetailsClient)
class SteamAppDetailsClient(ISteamAppDetailsClient):
    def __init__(
        self,
        http_client_pool: IHttpClientPool,
        logger_factory: ILoggerFactory,
        options: IOptions[SteamAppDetailsOptions]
    ) -> None:
        super().__init__()
        self.__http_client_pool = http_client_pool
        self.__log = logger_factory.create(SteamAppDetailsOptions)
        self.__options = options
        self.__circuit_breaker = AsyncCircuitBreakerPolicy[str, Any](
            options.value.CircuitBreakerFailureThreshold,
            options.value.CircuitBreakerRecoveryTime,
            SteamAppDetailsClient.__on_circuit_broken
        )

    async def get_app_details(self, identifier: str) -> SteamAppDetails | None:
        try:
            response = await self.__circuit_breaker.execute(
                lambda s: self.__http_client_pool.get(s),
                build_url(self.__options.value.BaseUrl, (), { "appids": identifier })
            )
        except HttpStatusError as error:
            self.__log.error("An HTTP error has occurred during a SteamAppDetails request", error)
            raise
        except CircuitBrokenError:
            raise
        except Exception as error:
            self.__log.error("An unexpected error has occurred during a SteamAppDetails request", error)
            raise

        if not response:
            return None

        appdetails = deserialize(dict[str, AppDetails], response)
        if (
            not appdetails
            or not (app := appdetails.get(identifier))
            or not app.success
        ):
            return None

        return SteamAppDetails(
            identifier=identifier,
            name=app.data.name,
            required_age=app.data.required_age,
            is_free=app.data.is_free,
            short_description=app.data.short_description,
            screenshot_urls=tuple(
                screenshot.path_full
                for screenshot in app.data.screenshots
            )
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
