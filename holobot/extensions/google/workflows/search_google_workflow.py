
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import (
    Choice, Cooldown, InteractionResponse, Option
)
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.network.exceptions import HttpStatusError
from ..enums import SearchType
from ..exceptions import SearchQuotaExhaustedError
from ..igoogle_client import IGoogleClient

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
        name="google",
        options=(
            Option("query", "The keywords to search for."),
            Option("type", "The type of the search.", is_mandatory=False, choices=(
                Choice("Text", "text"),
                Choice("Image", "image")
            ))
        ),
        cooldown=Cooldown(duration=20)
    )
    async def search_google(
        self,
        context: ServerChatInteractionContext,
        query: str,
        type: str | None = None
    ) -> InteractionResponse:
        search_type = SearchType.IMAGE if type == "image" else SearchType.TEXT
        try:
            results = await self.__google_client.search(search_type, query)
            if not results or not results[0].link:
                return InteractionResponse(
                    action=ReplyAction(content=self.__i18n_provider.get(
                        "extensions.google.search_google_workflow.no_results"
                    ))
                )

            link = results[0].link
            return InteractionResponse(action=ReplyAction(content=link))
        except InvalidOperationError:
            return InteractionResponse(
                action=ReplyAction(content=self.__i18n_provider.get("feature_disabled_error"))
            )
        except SearchQuotaExhaustedError:
            return InteractionResponse(
                action=ReplyAction(content=self.__i18n_provider.get(
                    "feature_quota_exhausted_error"
                ))
            )
        except HttpStatusError as error:
            self.__logger.error(
                "An error has occurred during a Google search HTTP request.",
                error
            )
            return InteractionResponse(
                action=ReplyAction(content=self.__i18n_provider.get(
                    "extensions.google.search_google_workflow.google_error"
                ))
            )
