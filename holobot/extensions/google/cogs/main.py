from .. import GoogleClientInterface
from ..enums import SearchType
from ..exceptions import SearchQuotaExhaustedError
from discord.ext.commands import Context
from discord.ext.commands.cog import Cog
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.core import cooldown, group
from discord.ext.commands.errors import CommandOnCooldown
from discord_slash import cog_ext, SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_choice, create_option
from holobot.discord.bot import Bot
from holobot.discord.sdk.utils import reply
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.logging import LogInterface
from holobot.sdk.network.exceptions import HttpStatusError
from typing import Optional, Union

class Google(Cog, name="Google"):
    def __init__(self, bot: Bot):
        super().__init__()
        self.__google_client = bot.service_collection.get(GoogleClientInterface)
        self.__log = bot.service_collection.get(LogInterface).with_name("Google", "Google")
    
    @group(aliases=["g"], brief="A group of Google Search Engine related commands.")
    async def google(self, context: Context):
        if not context.invoked_subcommand:
            await context.reply("You have to specify a sub-command!", delete_after=3)
    
    @cooldown(1, 10, BucketType.member)
    @google.command(aliases=["s"], brief="Searches Google with the specified keywords.")
    async def search(self, context: Context, *, keywords: str):
        await self.__search(context, SearchType.TEXT, keywords)
    
    @cooldown(1, 10, BucketType.member)
    @google.command(aliases=["i"], brief="Searches Google Images with the specified keywords.")
    async def image(self, context: Context, *, keywords: str):
        await self.__search(context, SearchType.IMAGE, keywords) 

    @cog_ext.cog_slash(name="google", description="Searches Google with a specific query.", options=[
        create_option("query", "The keywords to search for.", SlashCommandOptionType.STRING, True),
        create_option("type", "The type of the search.", SlashCommandOptionType.STRING, False, choices=[
            create_choice("text", "Text"),
            create_choice("image", "Image")
        ])
    ])
    async def slash_search(self, context: SlashContext, query: str, type: Optional[str] = None):
        search_type = SearchType.IMAGE if type == "image" else SearchType.TEXT
        await self.__search(context, search_type, query)
    
    async def __search(self, context: Union[Context, SlashContext], search_type: SearchType, query: str) -> None:
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
    
    @search.error
    @image.error
    async def on_error(self, context: Context, error):
        if isinstance(error, CommandOnCooldown):
            await context.reply(f"You're too fast! ({int(error.retry_after)} seconds cooldown)", delete_after=5)
            return
        raise error

def setup(bot: Bot):
    bot.add_cog(Google(bot))
