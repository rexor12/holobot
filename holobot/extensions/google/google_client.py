from .google_client_interface import GoogleClientInterface
from .enums import SearchType
from .exceptions import SearchQuotaExhaustedError
from .models import SearchResult
from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.ioc import ServiceCollectionInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from holobot.sdk.network import HttpClientPoolInterface
from holobot.sdk.network.exceptions import HttpStatusError, TooManyRequestsError
from typing import Dict, Tuple

GCS_API_KEY = "GoogleSearchApiKey"
GCS_ENGINE_ID = "GoogleSearchEngineId"
TEXT_SEARCH_TYPE = "SEARCH_TYPE_UNDEFINED"

@injectable(GoogleClientInterface)
class GoogleClient(GoogleClientInterface):
    search_types: Dict[SearchType, str] = {
        SearchType.TEXT: TEXT_SEARCH_TYPE,
        SearchType.IMAGE: "IMAGE"
    }

    def __init__(self, services: ServiceCollectionInterface) -> None:
        super().__init__()
        self.__configurator: ConfiguratorInterface = services.get(ConfiguratorInterface)
        self.__http_client_pool: HttpClientPoolInterface = services.get(HttpClientPoolInterface)
        self.__log: LogInterface = services.get(LogInterface)
        self.__api_key: str = self.__configurator.get("Google", GCS_API_KEY, "")
        self.__engine_id: str = self.__configurator.get("Google", GCS_ENGINE_ID, "")

    async def search(self, search_type: SearchType, query: str, max_results: int = 1) -> Tuple[SearchResult, ...]:
        if not self.__api_key or not self.__engine_id:
            raise InvalidOperationError("Google searches aren't configured.")
        if not query:
            raise ValueError("The query must not be empty.")
        
        try:
            # TODO Use circuit breaker.
            response = await self.__http_client_pool.get("https://www.googleapis.com/customsearch/v1", {
                "key": self.__api_key,
                "cx": self.__engine_id,
                "searchType": GoogleClient.search_types.get(search_type, TEXT_SEARCH_TYPE),
                "num": max_results,
                "q": query
            })
        except TooManyRequestsError:
            raise SearchQuotaExhaustedError
        except HttpStatusError as error:
            self.__log.error("An HTTP error has occurred during a Google search request.", error)
            raise
        except Exception as error:
            self.__log.error(f"An unexpected error has occurred during a Google request. ({type(error)})", error)
            raise
        
        if len(results := response.get("items", [])) == 0:
            return ()
        
        return tuple([SearchResult.from_json(result) for result in results])
