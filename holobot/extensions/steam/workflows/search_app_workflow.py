from datetime import timedelta
from math import ceil
from typing import Any, cast

from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.exceptions import FeatureDisabledError
from holobot.discord.sdk.models import Embed, EmbedFooter, InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import (
    ComponentBase, LayoutBase, Paginator
)
from holobot.discord.sdk.workflows.interactables.components.models import PagerState
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.models import (
    Choice, Cooldown, InteractionResponse, Option
)
from holobot.extensions.steam import IAppDataProvider
from holobot.extensions.steam.models import SteamOptions
from holobot.sdk.caching import IObjectCache, SlidingExpirationCacheEntryPolicy
from holobot.sdk.configs import IOptions
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.network.exceptions import HttpStatusError, TooManyRequestsError
from holobot.sdk.utils.type_utils import UNDEFINED, UndefinedOrNoneOr
from holobot.sdk.utils.uuid_utils import random_uuid

@injectable(IWorkflow)
class SearchAppWorkflow(WorkflowBase):
    def __init__(
        self,
        app_provider: IAppDataProvider,
        cache: IObjectCache,
        options: IOptions[SteamOptions],
        i18n_provider: II18nProvider,
        logger_factory: ILoggerFactory
    ) -> None:
        super().__init__()
        self.__cache = cache
        self.__app_provider = app_provider
        self.__options = options
        self.__i18n_provider = i18n_provider
        self.__logger = logger_factory.create(SearchAppWorkflow)

    @command(
        description="Searches Steam's application diectory. Results expire after a while.",
        name="search",
        group_name="steam",
        options=(
            Option("name", "The name of the application."),
        ),
        cooldown=Cooldown(duration=20),
        defer_type=DeferType.DEFER_MESSAGE_CREATION
    )
    async def search_steam_apps(
        self,
        context: InteractionContext,
        name: str,
        defer_type=DeferType.DEFER_MESSAGE_CREATION
    ) -> InteractionResponse:
        try:
            result = await self.__app_provider.find(name)
            if not result:
                return self._reply(content="No result.")

            return self._reply(
                content=f"{result.identifier}: {result.name}"
            )
            # result = await self.__search(search_type, query)
            # if not result.items:
            #     return self._reply(
            #         content=self.__i18n_provider.get(
            #             "extensions.google.search_google_workflow.no_results"
            #         )
            #     )

            # result_id = await self.__save_search_result(
            #     context.author_id,
            #     query,
            #     search_type,
            #     result
            # )

            # content, embed, components = await self.__create_page(context.author_id, result_id, 0)

            # return self._reply(
            #     content=content if isinstance(content, str) else None,
            #     embed=embed if isinstance(embed, Embed) else None,
            #     components=components
            # )
        except FeatureDisabledError:
            return self._reply(content=self.__i18n_provider.get("feature_disabled_error"))
        except TooManyRequestsError:
            return self._reply(content=self.__i18n_provider.get("feature_quota_exhausted_error"))
        except HttpStatusError as error:
            self.__logger.error(
                "An error has occurred during a Google search HTTP request.",
                error
            )
            return self._reply(content=self.__i18n_provider.get("extensions.google.google_error"))

    # @component(
    #     identifier="steamspagi",
    #     component_type=Paginator,
    #     defer_type=DeferType.DEFER_MESSAGE_UPDATE
    # )
    # async def change_page(
    #     self,
    #     context: InteractionContext,
    #     state: Any
    # ) -> InteractionResponse:
    #     if not isinstance(state, PagerState):
    #         return self._edit_message(
    #             content=self.__i18n_provider.get("interactions.invalid_interaction_data_error")
    #         )

    #     content, embed, components = await self.__create_page(
    #         state.owner_id,
    #         state.custom_data.get("r", ""),
    #         state.current_page
    #     )

    #     return self._edit_message(
    #         content=content,
    #         embed=embed,
    #         components=components
    #     )

    @staticmethod
    def __get_cache_key(user_id: str, results_id: str) -> str:
        return f"steam_app_search/{user_id}/{results_id}"

    # async def __save_search_result(
    #     self,
    #     author_id: str,
    #     query: str,
    #     result: SearchResult
    # ) -> str:
    #     result_id = random_uuid(8)
    #     await self.__cache.add_or_replace(
    #         SearchGoogleWorkflow.__get_cache_key(author_id, result_id),
    #         ExpandingSearchResult(
    #             query=query,
    #             search_type=search_type,
    #             total_result_count=result.total_result_count,
    #             available_result_count=min(
    #                 min(self.__options.value.MaxSearchResultsPerQuery, SearchGoogleWorkflow._GOOGLE_MAX_RESULTS),
    #                 result.total_result_count
    #             ),
    #             items=result.items,
    #             last_page=min(
    #                 SearchGoogleWorkflow._LAST_PAGE_INDEX,
    #                 ceil(result.total_result_count / 10)
    #             )
    #         ),
    #         SlidingExpirationCacheEntryPolicy(timedelta(
    #             seconds=self.__options.value.SearchResultExpirationTime
    #         ))
    #     )

    #     return result_id

    # async def __expand_search_result(
    #     self,
    #     expanding_result: ExpandingSearchResult
    # ) -> None:
    #     result = await self.__google_client.search(
    #         expanding_result.search_type,
    #         expanding_result.query,
    #         expanding_result.results_per_page,
    #         expanding_result.current_page + 1
    #     )

    #     expanding_result.current_page += 1
    #     for item in result.items:
    #         if SearchGoogleWorkflow._HTTP_REGEX.match(item.link):
    #             expanding_result.items.append(item)

    # async def __create_page(
    #     self,
    #     owner_id: str,
    #     results_id: str,
    #     result_index: int
    # ) -> tuple[
    #         UndefinedOrNoneOr[str],
    #         UndefinedOrNoneOr[Embed],
    #         ComponentBase | list[LayoutBase] | None
    #     ]:
    #     cache_key = SearchGoogleWorkflow.__get_cache_key(owner_id, results_id)
    #     if not (results := cast(ExpandingSearchResult, await self.__cache.get(cache_key))):
    #         return (
    #             UNDEFINED,
    #             UNDEFINED,
    #             None
    #         )

    #     async with results.lock:
    #         # If we reached the end of the cached results, try to fetch more.
    #         result_count = len(results.items)
    #         if result_index >= result_count:
    #             if results.current_page < results.last_page:
    #                 await self.__expand_search_result(results)
    #             else:
    #                 result_index = result_count - 1

    #         # Due to filtering we may run out of results, so we give up trying.
    #         result_count = len(results.items)
    #         if result_index >= result_count:
    #             result_index = result_count - 1
    #             out_of_results = True
    #         else:
    #             out_of_results = False

    #         result = results.items[result_index]
    #         available_result_count = max(results.available_result_count, len(results.items))
    #         content, embed = self.__create_page_view(
    #             result.title,
    #             result.link,
    #             result_index,
    #             available_result_count,
    #             out_of_results,
    #             results.search_type
    #         )

    #         return (
    #             content,
    #             embed,
    #             Paginator(
    #                 id="gsearchpagi",
    #                 owner_id=owner_id,
    #                 current_page=result_index,
    #                 page_size=1,
    #                 total_count=available_result_count,
    #                 custom_data={ "r": results_id }
    #             ) if available_result_count > 1 else None
    #         )

    # def __create_page_view(
    #     self,
    #     result_title: str,
    #     result_url: str,
    #     result_index: int,
    #     available_result_count: int,
    #     out_of_results: bool,
    #     search_type: SearchType
    # ) -> tuple[str | None, Embed | None]:
    #     if search_type == SearchType.IMAGE:
    #         return (
    #             None,
    #             self.__create_image_embed(
    #                 result_title,
    #                 result_url,
    #                 result_index,
    #                 available_result_count,
    #                 out_of_results
    #             )
    #         )

    #     l10n_context = {
    #         "result_index": result_index + 1,
    #         "result_count": available_result_count,
    #         "url": result_url
    #     }
    #     if out_of_results:
    #         return (
    #             self.__i18n_provider.get(
    #                 "extensions.google.search_google_workflow.text_result_with_error",
    #                 l10n_context
    #             ),
    #             None
    #         )
    #     else:
    #         return (
    #             self.__i18n_provider.get(
    #                 "extensions.google.search_google_workflow.text_result",
    #                 l10n_context
    #             ),
    #             None
    #         )

    # def __create_image_embed(
    #     self,
    #     result_title: str,
    #     result_url: str,
    #     result_index: int,
    #     result_count: int,
    #     out_of_results: bool
    # ) -> Embed:
    #     if out_of_results:
    #         description = self.__i18n_provider.get(
    #             "extensions.google.search_google_workflow.embed_description_with_error",
    #             { "result_title": result_title }
    #         )
    #     else:
    #         description = result_title

    #     return Embed(
    #         title=self.__i18n_provider.get(
    #             "extensions.google.search_google_workflow.embed_title"
    #         ),
    #         description=description,
    #         image_url=result_url ,
    #         footer=EmbedFooter(
    #             text=self.__i18n_provider.get(
    #                 "extensions.google.search_google_workflow.embed_footer",
    #                 {
    #                     "result_index": result_index + 1,
    #                     "result_count": result_count
    #                 }
    #             )
    #         )
    #     )
