from .. import GoogleClientInterface
from ..enums import SearchType
from ..exceptions import SearchQuotaExhaustedError
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.models import Choice, CommandResponse, Option, ServerChatInteractionContext
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from holobot.sdk.network.exceptions import HttpStatusError
from typing import Optional

@injectable(CommandInterface)
class SearchGoogleCommand(CommandBase):
    def __init__(self, google_client: GoogleClientInterface, log: LogInterface) -> None:
        super().__init__("google")
        self.__google_client = google_client
        self.__log = log.with_name("Google", "SearchGoogleCommand")
        self.description = "Searches Google with a specific query."
        self.options = [
            Option("query", "The keywords to search for."),
            Option("type", "The type of the search.", is_mandatory=False, choices=[
                Choice("Text", "text"),
                Choice("Image", "image")
            ])
        ]
    
    async def execute(self, context: ServerChatInteractionContext, query: str, type: Optional[str] = None) -> CommandResponse:
        search_type = SearchType.IMAGE if type == "image" else SearchType.TEXT
        try:
            results = await self.__google_client.search(search_type, query)
            if len(results) == 0:
                return CommandResponse(
                    action=ReplyAction(content="There are no good results for your query. Please, try something else in a bit.")
                )
            link = results[0].link
            return CommandResponse(
                action=ReplyAction(content=link if link else "An unexpected Google error has occurred. Please, try again later.")
            )
        except InvalidOperationError:
            return CommandResponse(
                action=ReplyAction(content="Google Search isn't configured. Please, contact your server administrator.")
            )
        except SearchQuotaExhaustedError:
            return CommandResponse(
                action=ReplyAction(content="The daily search quota has been used up for the bot. Please, try again later or contact your server administrator.")
            )
        except HttpStatusError as error:
            self.__log.error("An error has occurred during a Google search HTTP request.", error)
            return CommandResponse(
                action=ReplyAction(content="An unexpected Google error has occurred. Please, try again later.")
            )
