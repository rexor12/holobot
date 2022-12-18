from typing import Any

from holobot.extensions.general.models import WaifuPicsOptions
from holobot.sdk.configs import IOptions
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.network import IHttpClientPool
from holobot.sdk.network.exceptions import HttpStatusError, TooManyRequestsError
from holobot.sdk.network.resilience import AsyncCircuitBreakerPolicy, CombinedPolicyBuilder
from holobot.sdk.network.resilience.exceptions import CircuitBrokenError
from holobot.sdk.serialization.json_serializer import deserialize
from holobot.sdk.utils import assert_not_none
from .dtos import WaifuPicsBatchResult
from .iwaifu_pics_client import IWaifuPicsClient

@injectable(IWaifuPicsClient)
class WaifuPicsClient(IWaifuPicsClient):
    def __init__(
        self,
        http_client_pool: IHttpClientPool,
        logger_factory: ILoggerFactory,
        options: IOptions[WaifuPicsOptions]
    ) -> None:
        super().__init__()
        self.__http_client_pool = http_client_pool
        self.__log = logger_factory.create(WaifuPicsClient)
        self.__options = options
        self.__resilience_policy = (CombinedPolicyBuilder[str, Any]()
            .circuit_breaker(
                options.value.CircuitBreakerFailureThreshold,
                options.value.CircuitBreakerRecoveryTime,
                WaifuPicsClient.__on_circuit_broken
            )
            .rate_limiter(
                options.value.RateLimiterRequestsPerInterval,
                options.value.RateLimiterInterval
            )
            .build()
        )

    async def get_batch(
        self,
        category: str,
    ) -> tuple[str, ...]:
        assert_not_none(category, "category")

        options = self.__options.value
        if not options.Url:
            return ()

        try:
            response = await self.__resilience_policy.execute(
                lambda url: self.__http_client_pool.post(url, {}),
                f"{options.Url}{category}"
            )
        except TooManyRequestsError as error:
            self.__log.warning("Rate limited by waifu.pics", exception=error)
            raise
        except HttpStatusError as error:
            self.__log.error("An HTTP error has occurred during a waifu.pics request", error)
            raise
        except CircuitBrokenError:
            raise
        except Exception as error:
            self.__log.error("An unexpected error has occurred during a waifu.pics request", error)
            raise

        dto = deserialize(WaifuPicsBatchResult, response)
        return tuple(dto.files) if dto else ()

    @staticmethod
    async def __on_circuit_broken(
        circuit_breaker: AsyncCircuitBreakerPolicy[str, Any],
        error: Exception
    ) -> int:
        if (isinstance(error, TooManyRequestsError)
            and error.retry_after
            and isinstance(error.retry_after, int)
        ):
            return error.retry_after
        return circuit_breaker.recovery_timeout
