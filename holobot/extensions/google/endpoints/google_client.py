from typing import Any

from holobot.extensions.google.enums import SearchType
from holobot.extensions.google.exceptions import QuotaExhaustedError
from holobot.extensions.google.models import (
    GoogleClientOptions, Language, SearchResult, SearchResultItem, Translation
)
from holobot.sdk.configs import IOptions
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.network import HttpClientPoolInterface
from holobot.sdk.network.exceptions import HttpStatusError, TooManyRequestsError
from holobot.sdk.network.resilience import AsyncCircuitBreakerPolicy
from holobot.sdk.network.resilience.exceptions import CircuitBrokenError
from holobot.sdk.serialization.json_serializer import deserialize
from .dtos.search_response import SearchResponse
from .igoogle_client import IGoogleClient
from .translation_endpoint import TranslationEndpoint

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
        self.__translation_endpoint = TranslationEndpoint(logger_factory, options)

    async def search(
        self,
        search_type: SearchType,
        query: str,
        max_results: int = 1,
        page_index: int = 1
    ) -> SearchResult:
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
                        "q": query,
                        "start": page_index * max_results
                    }
                )
            )
        except TooManyRequestsError as error:
            raise QuotaExhaustedError from error
        except HttpStatusError as error:
            self.__log.error("An HTTP error has occurred during a Google search request", error)
            raise
        except CircuitBrokenError:
            raise
        except Exception as error:
            self.__log.error("An unexpected error has occurred during a Google request", error)
            raise

        response_dto = deserialize(SearchResponse, response)
        if not response_dto:
            return SearchResult()

        return SearchResult(
            total_result_count=response_dto.searchInformation.totalResults,
            items=[
                SearchResultItem(
                    title=item.title,
                    link=item.link,
                    fileSize=item.image.byteSize
                )
                for item in response_dto.items
            ]
        )

    async def translate_text(
        self,
        text: str,
        target_language: str,
        source_language: str | None = None
    ) -> Translation | None:
        return await self.__translation_endpoint.translate_text(
            text,
            target_language,
            source_language
        )

    async def get_languages(self) -> dict[str, Language]:
        return await self.__translation_endpoint.get_languages()

    async def get_language_by_code(self, code: str) -> Language | None:
        return await self.__translation_endpoint.get_language_by_code(code)

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
