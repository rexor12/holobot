from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import (
    Choice, Cooldown, InteractionResponse, Option
)
from holobot.extensions.google.endpoints import IGoogleClient
from holobot.extensions.google.enums import SearchType
from holobot.extensions.google.exceptions import QuotaExhaustedError
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.network.exceptions import HttpStatusError

@injectable(IWorkflow)
class SearchGoogleWorkflow(WorkflowBase):
    def __init__(
        self,
        google_client: IGoogleClient,
        i18n_provider: II18nProvider,
        logger_factory: ILoggerFactory
    ) -> None:
        super().__init__()
        self.__google_client = google_client
        self.__i18n_provider = i18n_provider
        self.__logger = logger_factory.create(SearchGoogleWorkflow)

    @command(
        description="Searches Google with a specific query.",
        name="search",
        group_name="google",
        options=(
            Option("query", "The keywords to search for."),
            Option("type", "The type of the search.", is_mandatory=False, choices=(
                Choice("Text", "text"),
                Choice("Image", "image")
            ))
        ),
        cooldown=Cooldown(duration=20),
        defer_type=DeferType.DEFER_MESSAGE_CREATION
    )
    async def search_google(
        self,
        context: InteractionContext,
        query: str,
        type: str | None = None
    ) -> InteractionResponse:
        search_type = SearchType.IMAGE if type == "image" else SearchType.TEXT
        try:
            results = await self.__google_client.search(search_type, query)
            if not results or not results[0].link:
                return self._reply(
                    content=self.__i18n_provider.get(
                        "extensions.google.search_google_workflow.no_results"
                    )
                )

            link = results[0].link
            return self._reply(content=link)
        except InvalidOperationError:
            return self._reply(content=self.__i18n_provider.get("feature_disabled_error"))
        except QuotaExhaustedError:
            return self._reply(content=self.__i18n_provider.get("feature_quota_exhausted_error"))
        except HttpStatusError as error:
            self.__logger.error(
                "An error has occurred during a Google search HTTP request.",
                error
            )
            return self._reply(content=self.__i18n_provider.get("extensions.google.google_error"))
