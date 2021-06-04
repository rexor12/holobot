from .. import GoogleClientInterface
from ..enums import SearchType
from ..exceptions import SearchQuotaExhaustedError
from discord.ext.commands import Context
from discord.ext.commands.cog import Cog
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.core import cooldown, group
from discord.ext.commands.errors import CommandOnCooldown
from holobot.discord.bot import Bot
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.logging import LogInterface
from holobot.sdk.network.exceptions import HttpStatusError

class Google(Cog, name="Google"):
    def __init__(self, bot: Bot):
        super().__init__()
        self.__google_client = bot.service_collection.get(GoogleClientInterface)
        self.__log = bot.service_collection.get(LogInterface)
    
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
    
    async def __search(self, context: Context, search_type: SearchType, query: str) -> None:
        try:
            results = await self.__google_client.search(search_type, query)
            if len(results) == 0:
                await context.reply("There are no good results for your query. Please, try something else in a bit.")
                return
            await context.reply(results[0].link)
        except InvalidOperationError:
            await context.reply("Google Search isn't configured. Please, contact your server administrator.")
        except SearchQuotaExhaustedError:
            await context.reply("The daily search quota has been used up for the bot. Please, try again later or contact your server administrator.")
        except HttpStatusError as error:
            self.__log.error("An error has occurred during a Google search HTTP request.", error)
            await context.reply("An unexpected Google error has occurred. Please, try again later.")

    @search.error
    @image.error
    async def on_error(self, context: Context, error):
        if isinstance(error, CommandOnCooldown):
            await context.send(f"{context.author.mention}, you're too fast! ({int(error.retry_after)} seconds cooldown)", delete_after=5)
            return
        raise error

def setup(bot: Bot):
    bot.add_cog(Google(bot))
