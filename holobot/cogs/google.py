from discord.ext.commands import Context
from discord.ext.commands.cog import Cog
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.core import cooldown, group
from discord.ext.commands.errors import CommandOnCooldown
from holobot.bot import Bot
from holobot.configs.configurator_interface import ConfiguratorInterface
from holobot.logging.log_interface import LogInterface
from holobot.network.exceptions.http_status_error import HttpStatusError
from holobot.network.http_client_pool_interface import HttpClientPoolInterface
from urllib.parse import quote_plus

GCS_API_KEY = "GoogleSearchApiKey"
GCS_ENGINE_ID = "GoogleSearchEngineId"
TEXT_SEARCH_TYPE = "SEARCH_TYPE_UNDEFINED"
IMAGE_SEARCH_TYPE = "IMAGE"

class Google(Cog, name="Google"):
    def __init__(self, bot: Bot):
        super().__init__()
        self.__bot = bot
        self.__http_client_pool = bot.service_collection.get(HttpClientPoolInterface)
        self.__configurator = bot.service_collection.get(ConfiguratorInterface)
        self.__log = bot.service_collection.get(LogInterface)
    
    @group(aliases=["g"], brief="A group of Google Search Engine related commands.")
    async def google(self, context: Context):
        if not context.invoked_subcommand:
            await context.send(f"{context.author.mention}, you have to specify a sub-command!", delete_after=3)
    
    @cooldown(1, 10, BucketType.member)
    @google.command(aliases=["s"], brief="Searches Google with the specified keywords.")
    async def search(self, context: Context, *, keywords: str):
        await self.__search(context, TEXT_SEARCH_TYPE, keywords)
    
    @cooldown(1, 10, BucketType.member)
    @google.command(aliases=["i"], brief="Searches Google Images with the specified keywords.")
    async def image(self, context: Context, *, keywords: str):
        await self.__search(context, IMAGE_SEARCH_TYPE, keywords)

    @search.error
    @image.error
    async def on_error(self, context: Context, error):
        if isinstance(error, CommandOnCooldown):
            await context.send(f"{context.author.mention}, you're too fast! ({int(error.retry_after)} seconds cooldown)", delete_after=5)
            return
        raise error

    async def __search(self, context: Context, search_type: str, keywords: str):
        if not keywords or len(keywords) == 0:
            await context.send(f"{context.author.mention}, you have to specify at least one keyword!")
            self.search.reset_cooldown(context)
            return
        api_key = self.__configurator.get("General", GCS_API_KEY, "")
        engine_id = self.__configurator.get("General", GCS_ENGINE_ID, "")
        if not api_key or not engine_id:
            await context.send(f"{context.author.mention}, the bot doesn't have Google searches configured. Please, contact the server administrator.")
            return
        try:
            # TODO Use circuit breaker.
            response = await self.__http_client_pool.get(f"https://www.googleapis.com/customsearch/v1", {
                "key": api_key,
                "cx": engine_id,
                "searchType": search_type,
                "num": 1,
                "q": quote_plus(keywords)
            })
        except HttpStatusError as error:
            self.__log.error("An error has occurred during a Google search HTTP request.", error)
            if error.status_code == 429:
                await context.send(f"{context.author.mention}, the daily search quota has been used up for the bot. Please, try again tomorrow or contact your server administrator.")
            else: await context.send(f"{context.author.mention}, encountered an unexpected error. Please, try again later.")
            return
        if len(results := response.get("items", [])) == 0:
            await context.send(f"{context.author.mention}, there are no search results for your query. Please, try something else.")
            return
        if not (link := results[0].get("link", None)):
            await context.send(f"{context.author.mention}, Google has returned an unexpected response. Please, try again later.")
            return
        await context.send(link)

def setup(bot: Bot):
    bot.add_cog(Google(bot))