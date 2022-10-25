from typing import Any

from holobot.sdk.configs import IOptions
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.network import HttpClientPoolInterface
from holobot.sdk.network.exceptions import HttpStatusError, TooManyRequestsError
from holobot.sdk.network.resilience import AsyncCircuitBreakerPolicy
from holobot.sdk.network.resilience.exceptions import CircuitBrokenError
from .enums import SearchType
from .exceptions import SearchQuotaExhaustedError
from .igoogle_client import IGoogleClient
from .models import GoogleClientOptions, SearchResult

TEXT_SEARCH_TYPE = "SEARCH_TYPE_UNDEFINED"

@injectable(IGoogleClient)
class GoogleClient(IGoogleClient):
    search_types: dict[SearchType, str] = {
        SearchType.TEXT: TEXT_SEARCH_TYPE,
        SearchType.IMAGE: "IMAGE"
    }

    def __init__(
        self,
        http_client_pool: HttpClientPoolInterface,
        logger_factory: ILoggerFactory,
        options: IOptions[GoogleClientOptions]
    ) -> None:
        super().__init__()
        self.__http_client_pool = http_client_pool
        self.__options = options.value
        self.__log = logger_factory.create(GoogleClient)
        self.__circuit_breaker = AsyncCircuitBreakerPolicy[tuple[str, dict[str, Any]], Any](
            options.value.CircuitBreakerFailureThreshold,
            options.value.CircuitBreakerRecoveryTime,
            GoogleClient.__on_circuit_broken
        )

    async def search(
        self,
        search_type: SearchType,
        query: str,
        max_results: int = 1
    ) -> tuple[SearchResult, ...]:
        api_key = self.__options.GoogleSearchApiKey
        engine_id = self.__options.GoogleSearchEngineId
        if not api_key or not engine_id:
            raise InvalidOperationError("Google searches aren't configured.")
        if not query:
            raise ValueError("The query must not be empty.")

        try:
            response = await self.__circuit_breaker(
                lambda s: self.__http_client_pool.get(s[0], s[1]),
                (
                    "https://www.googleapis.com/customsearch/v1",
                    {
                        "key": api_key,
                        "cx": engine_id,
                        "searchType": GoogleClient.search_types.get(search_type, TEXT_SEARCH_TYPE),
                        "num": max_results,
                        "q": query
                    }
                )
            )
        except TooManyRequestsError as error:
            raise SearchQuotaExhaustedError from error
        except HttpStatusError as error:
            self.__log.error("An HTTP error has occurred during a Google search request.", error)
            raise
        except CircuitBrokenError:
            raise
        except Exception as error:
            self.__log.error("An unexpected error has occurred during a Google request", error)
            raise

        if not (results := response.get("items")):
            return ()

        return tuple(map(SearchResult.from_json, results))

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
