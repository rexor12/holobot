from discord.enums import ActivityType
from discord.ext.commands import Context
from discord.ext.commands.cog import Cog
from discord.ext.commands.core import group
from discord.ext.commands.errors import CommandInvokeError, ExtensionAlreadyLoaded, ExtensionFailed, ExtensionNotFound, ExtensionNotLoaded, NoEntryPointError
from holobot.discord.bot import Bot
from holobot.discord.decorators import is_developer
from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.exceptions import AuthorizationError
from holobot.sdk.logging import LogInterface
from holobot.sdk.logging.enums import LogLevel
from typing import Optional

class Development(Cog, name="Development"):
    def __init__(self, bot: Bot):
        super().__init__()
        self.__bot = bot
        self.__configurator = bot.service_collection.get(ConfiguratorInterface)
        self.__log = bot.service_collection.get(LogInterface).with_name("Dev", "Development")

    @group(hidden=True)
    async def dev(self, context: Context):
        if not context.invoked_subcommand:
            await context.reply("You have to specify a sub-command!", delete_after=3)
    
    @dev.command(hidden=True)
    @is_developer
    async def say(self, context: Context, *, message: str):
        await context.message.delete()
        await context.send(message)
    
    @dev.command(hidden=True)
    @is_developer
    async def load(self, context: Context, name: str):
        if name == self.__module__:
            await context.reply(f"You can't load the extension '{name}'.")
            return
        if await self.__load(context, name):
            await context.reply(f"The extension '{name}' has been **loaded**.")
    
    @dev.command(hidden=True)
    @is_developer
    async def reload(self, context: Context, name: str):
        if name == self.__module__:
            await context.reply(f"You can't reload the extension '{name}'.")
            return
        if await self.__unload(context, name) and await self.__load(context, name):
            await context.reply(f"The extension '{name}' has been **reloaded**.")
    
    @dev.command(hidden=True)
    @is_developer
    async def unload(self, context: Context, name: str):
        if name == self.__module__:
            await context.reply(f"You can't unload the extension '{name}'.")
            return
        if await self.__unload(context, name):
            await context.reply(f"The extension '{name}' has been **unloaded**.")

    @dev.command(hidden=True)
    @is_developer
    async def log_level(self, context: Context, log_level: str):
        self.__log.set_global_log_level(LogLevel.parse(log_level))
        await context.reply("The log level has been changed.")
    
    # This is an extremely dangerous piece of code because it evaluates ANY expression.
    # Use it at your own risk only and never in a production environment!
    @dev.command(hidden=True)
    @is_developer
    async def eval(self, context: Context, *, expression: str):
        if not self.__configurator.get("General", "IsDebug", False):
            self.__log.warning(f"The user '{context.author.id}' attempted to evaluate arbitrary code, but debug mode is disabled.")
            return
        self.__log.info(f"Evaluating the following expression:\n{expression}")
        eval(expression)
    
    @dev.command(hidden=True)
    @is_developer
    async def ping(self, context: Context):
        latency = self.__bot.latency * 1000
        await context.reply(f"Pong! ({latency:,.2f}ms)")
    
    @dev.command(aliases=["status"], hidden=True)
    @is_developer
    async def set_status_text(self, context: Context, *, text: str):
        await self.__bot.set_status_text(ActivityType.watching, text)
        self.__log.info(f"Changed status text to '{text}'.")
    
    async def __load(self, context: Context, name: str) -> bool:
        reason: Optional[str] = None
        try:
            self.__bot.load_extension(name)
            return True
        except ExtensionNotFound:
            reason = "it cannot be found"
        except ExtensionAlreadyLoaded:
            reason = "it is already loaded"
        except NoEntryPointError:
            reason = "it is invalid"
        except ExtensionFailed as error:
            reason = "an error has occurred"
            self.__log.error("An extension has failed while being loaded.", error)
        await context.reply(f"Failed to load the extension '{name}', because {reason}.")
        return False
    
    async def __unload(self, context: Context, name: str):
        try:
            self.__bot.unload_extension(name)
            return True
        except ExtensionNotLoaded:
            await context.reply(f"The extension '{name}' isn't loaded.")
        return False

    @say.error
    @unload.error
    @load.error
    @reload.error
    @log_level.error
    @eval.error
    @ping.error
    @set_status_text.error
    async def on_error(self, context: Context, error):
        if isinstance(error, CommandInvokeError) and isinstance(error.original, AuthorizationError):
            self.__log.warning(f"The unauthorized user with the identifier '{context.author.id}' tried to execute '{context.command}'.")
            return
        self.__log.error(f"An error has occurred while executing the command '{context.command}'.", error)
        await context.author.send(f"Your command '{context.command}' generated the following error: {error}")
        await context.reply("An error has occurred while executing your command. A DM has been sent to you with the details.")

def setup(bot: Bot):
    bot.add_cog(Development(bot))
