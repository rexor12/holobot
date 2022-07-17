from typing import Optional

from ..igoogle_client import IGoogleClient
from ..enums import SearchType
from ..exceptions import SearchQuotaExhaustedError
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import Choice, InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from holobot.sdk.network.exceptions import HttpStatusError

@injectable(IWorkflow)
class SearchGoogleWorkflow(WorkflowBase):
    def __init__(
        self,
        google_client: IGoogleClient,
        log: LogInterface
    ) -> None:
        super().__init__()
        self.__google_client: IGoogleClient = google_client
        self.__log: LogInterface = log.with_name("Google", "SearchGoogleWorkflow")

    @command(
        description="Searches Google with a specific query.",
        name="google",
        options=(
            Option("query", "The keywords to search for."),
            Option("type", "The type of the search.", is_mandatory=False, choices=(
                Choice("Text", "text"),
                Choice("Image", "image")
            ))
        )
    )
    async def search_google(
        self,
        context: ServerChatInteractionContext,
        query: str,
        type: Optional[str] = None
    ) -> InteractionResponse:
        search_type = SearchType.IMAGE if type == "image" else SearchType.TEXT
        try:
            results = await self.__google_client.search(search_type, query)
            if len(results) == 0:
                return InteractionResponse(
                    action=ReplyAction(content="There are no good results for your query. Please, try something else in a bit.")
                )

            link = results[0].link
            return InteractionResponse(action=ReplyAction(
                content=link or "An unexpected Google error has occurred. Please, try again later."
            ))
        except InvalidOperationError:
            return InteractionResponse(
                action=ReplyAction(content="Google Search isn't configured. Please, contact your server administrator.")
            )
        except SearchQuotaExhaustedError:
            return InteractionResponse(
                action=ReplyAction(content=(
                    "The daily search quota has been used up for the bot."
                    " Please, try again later or contact your server administrator."
                ))
            )
        except HttpStatusError as error:
            self.__log.error("An error has occurred during a Google search HTTP request.", error)
            return InteractionResponse(
                action=ReplyAction(content="An unexpected Google error has occurred. Please, try again later.")
            )
