from .. import GoogleClientInterface
from ..enums import SearchType
from ..exceptions import SearchQuotaExhaustedError
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_choice, create_option
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.utils import reply
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
            create_option("query", "The keywords to search for.", SlashCommandOptionType.STRING, True),
            create_option("type", "The type of the search.", SlashCommandOptionType.STRING, False, choices=[
                create_choice("text", "Text"),
                create_choice("image", "Image")
            ])
        ]
    
    async def execute(self, context: SlashContext, query: str, type: Optional[str] = None):
        search_type = SearchType.IMAGE if type == "image" else SearchType.TEXT
        try:
            results = await self.__google_client.search(search_type, query)
            if len(results) == 0:
                await reply(context, "There are no good results for your query. Please, try something else in a bit.")
                return
            link = results[0].link
            if not link:
                await reply(context, "An unexpected Google error has occurred. Please, try again later.")
            else: await reply(context, link)
        except InvalidOperationError:
            await reply(context, "Google Search isn't configured. Please, contact your server administrator.")
        except SearchQuotaExhaustedError:
            await reply(context, "The daily search quota has been used up for the bot. Please, try again later or contact your server administrator.")
        except HttpStatusError as error:
            self.__log.error("An error has occurred during a Google search HTTP request.", error)
            await reply(context, "An unexpected Google error has occurred. Please, try again later.")
