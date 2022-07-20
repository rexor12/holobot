from .igoogle_client import IGoogleClient
from .enums import SearchType
from .exceptions import SearchQuotaExhaustedError
from .models import SearchResult
from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from holobot.sdk.network import HttpClientPoolInterface
from holobot.sdk.network.exceptions import HttpStatusError, TooManyRequestsError
from holobot.sdk.network.resilience import AsyncCircuitBreaker
from holobot.sdk.network.resilience.exceptions import CircuitBrokenError
from typing import Dict, Tuple

CONFIG_SECTION = "Google"
GCS_API_KEY = "GoogleSearchApiKey"
GCS_ENGINE_ID = "GoogleSearchEngineId"
CIRCUIT_BREAKER_FAILURE_THRESHOLD_PARAMETER = "CircuitBreakerFailureThreshold"
CIRCUIT_BREAKER_RECOVERY_TIME_PARAMETER = "CircuitBreakerRecoveryTime"
TEXT_SEARCH_TYPE = "SEARCH_TYPE_UNDEFINED"

@injectable(IGoogleClient)
class GoogleClient(IGoogleClient):
    search_types: Dict[SearchType, str] = {
        SearchType.TEXT: TEXT_SEARCH_TYPE,
        SearchType.IMAGE: "IMAGE"
    }

    def __init__(self, configurator: ConfiguratorInterface, http_client_pool: HttpClientPoolInterface, log: LogInterface) -> None:
        super().__init__()
        self.__configurator: ConfiguratorInterface = configurator
        self.__http_client_pool: HttpClientPoolInterface = http_client_pool
        self.__log: LogInterface = log.with_name("Google", "GoogleClient")
        self.__api_key: str = self.__configurator.get(CONFIG_SECTION, GCS_API_KEY, "")
        self.__engine_id: str = self.__configurator.get(CONFIG_SECTION, GCS_ENGINE_ID, "")
        self.__circuit_breaker: AsyncCircuitBreaker = GoogleClient.__create_circuit_breaker(self.__configurator)

    async def search(self, search_type: SearchType, query: str, max_results: int = 1) -> Tuple[SearchResult, ...]:
        if not self.__api_key or not self.__engine_id:
            raise InvalidOperationError("Google searches aren't configured.")
        if not query:
            raise ValueError("The query must not be empty.")

        try:
            response = await self.__circuit_breaker(
                self.__http_client_pool.get,
                "https://www.googleapis.com/customsearch/v1",
                {
                    "key": self.__api_key,
                    "cx": self.__engine_id,
                    "searchType": GoogleClient.search_types.get(search_type, TEXT_SEARCH_TYPE),
                    "num": max_results,
                    "q": query
                })
        except TooManyRequestsError as error:
            raise SearchQuotaExhaustedError from error
        except HttpStatusError as error:
            self.__log.error("An HTTP error has occurred during a Google search request.", error)
            raise
        except CircuitBrokenError:
            raise
        except Exception as error:
            self.__log.error(f"An unexpected error has occurred during a Google request. ({type(error)})", error)
            raise

        if len(results := response.get("items", [])) == 0:
            return ()

        return tuple(SearchResult.from_json(result) for result in results)
    
    @staticmethod
    def __create_circuit_breaker(configurator: ConfiguratorInterface) -> AsyncCircuitBreaker:
        return AsyncCircuitBreaker(
            configurator.get(CONFIG_SECTION, CIRCUIT_BREAKER_FAILURE_THRESHOLD_PARAMETER, 1),
            configurator.get(CONFIG_SECTION, CIRCUIT_BREAKER_RECOVERY_TIME_PARAMETER, 300),
            GoogleClient.__on_circuit_broken)
    
    @staticmethod
    async def __on_circuit_broken(circuit_breaker: AsyncCircuitBreaker, error: Exception) -> int:
        if (isinstance(error, TooManyRequestsError)
            and error.retry_after is not None
            and isinstance(error.retry_after, int)):
            return error.retry_after
        return circuit_breaker.recovery_timeout
