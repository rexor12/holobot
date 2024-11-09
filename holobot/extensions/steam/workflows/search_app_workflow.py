from datetime import timedelta
from typing import cast

from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.exceptions import FeatureDisabledError
from holobot.discord.sdk.models import Embed, InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import (
    ComponentBase, LayoutBase, Paginator
)
from holobot.discord.sdk.workflows.interactables.components.models import PaginatorState
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.models import (
    Choice, Cooldown, InteractionResponse, Option
)
from holobot.extensions.steam.endpoints import ISteamCommunityClient
from holobot.extensions.steam.models import GeneralOptions, SteamApp
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
        cache: IObjectCache,
        options: IOptions[GeneralOptions],
        i18n_provider: II18nProvider,
        logger_factory: ILoggerFactory,
        steam_community_client: ISteamCommunityClient
    ) -> None:
        super().__init__()
        self.__cache = cache
        self.__options = options
        self.__i18n_provider = i18n_provider
        self.__steam_community_client = steam_community_client
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
    ) -> InteractionResponse:
        try:
            matching_apps = await self.__steam_community_client.search_apps(name)
            if not matching_apps:
                return self._reply(
                    content=self.__i18n_provider.get(
                        "extensions.steam.search_app_workflow.no_results"
                    )
                )

            result_id = await self.__save_search_results(context.author_id, matching_apps)
            content, embed, components = await self.__create_page(context.author_id, result_id, 0)

            return self._reply(
                content=content if isinstance(content, str) else None,
                embed=embed if isinstance(embed, Embed) else None,
                components=components
            )
        except FeatureDisabledError:
            return self._reply(content=self.__i18n_provider.get("feature_disabled_error"))
        except TooManyRequestsError:
            return self._reply(content=self.__i18n_provider.get("feature_quota_exhausted_error"))
        except HttpStatusError as error:
            self.__logger.error(
                "An error has occurred during a Steam app search HTTP request.",
                error
            )
            return self._reply(content=self.__i18n_provider.get("extensions.steam.steam_api_error"))

    @component(identifier="stesearchpagi")
    async def change_page(
        self,
        context: InteractionContext,
        state: PaginatorState
    ) -> InteractionResponse:
        content, embed, components = await self.__create_page(
            state.owner_id,
            state.custom_data.get("r", ""),
            state.current_page
        )

        return self._edit_message(
            content=content,
            embed=embed,
            components=components
        )

    @staticmethod
    def __get_cache_key(user_id: int, results_id: str) -> str:
        return f"steam_app_search/{user_id}/{results_id}"

    async def __save_search_results(
        self,
        author_id: int,
        apps: tuple[SteamApp, ...]
    ) -> str:
        result_id = random_uuid(8)
        await self.__cache.add_or_replace(
            SearchAppWorkflow.__get_cache_key(author_id, result_id),
            apps,
            SlidingExpirationCacheEntryPolicy(timedelta(
                seconds=self.__options.value.SearchResultExpirationTime
            ))
        )

        return result_id

    async def __create_page(
        self,
        owner_id: int,
        results_id: str,
        result_index: int
    ) -> tuple[
            UndefinedOrNoneOr[str],
            UndefinedOrNoneOr[Embed],
            ComponentBase | list[LayoutBase] | None
        ]:
        cache_key = SearchAppWorkflow.__get_cache_key(owner_id, results_id)
        if not (results := cast(tuple[SteamApp, ...], await self.__cache.get(cache_key))):
            return (
                UNDEFINED,
                UNDEFINED,
                None
            )

        result_count = len(results)
        if result_index >= result_count or result_index < 0:
            result_index = 0

        result = results[result_index]

        return (
            self.__options.value.StoreAppPageUrl.format(appid=result.identifier),
            UNDEFINED,
            Paginator(
                id="stesearchpagi",
                owner_id=owner_id,
                current_page=result_index,
                page_size=1,
                total_count=result_count,
                custom_data={ "r": results_id }
            )
        )
