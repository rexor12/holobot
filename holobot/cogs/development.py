from discord.ext.commands import Context
from discord.ext.commands.cog import Cog
from discord.ext.commands.core import group
from discord.ext.commands.errors import ExtensionAlreadyLoaded, ExtensionFailed, ExtensionNotFound, ExtensionNotLoaded, NoEntryPointError
from holobot.bot import Bot
from holobot.cogs.utils.is_developer import is_developer
from holobot.configs.configurator_interface import ConfiguratorInterface
from holobot.exceptions.authorization_error import AuthorizationError
from holobot.logging.log_interface import LogInterface
from holobot.logging.log_level import LogLevel
from typing import Optional

class Development(Cog, name="Development"):
    def __init__(self, bot: Bot):
        super().__init__()
        self.__bot = bot
        self.__configurator = bot.service_collection.get(ConfiguratorInterface)
        self.__log = bot.service_collection.get(LogInterface)

    @group(hidden=True)
    async def dev(self, context: Context):
        if not context.invoked_subcommand:
            await context.send(f"{context.author.mention}, you have to specify a sub-command!", delete_after=3)
    
    @dev.command(hidden=True)
    @is_developer
    async def load(self, context: Context, name: str):
        if name == self.__module__:
            await context.send(f"{context.author.mention}, you can't load the extension '{name}'.")
            return
        if await self.__load(context, name):
            await context.send(f"{context.author.mention}, the extension '{name}' has been **loaded**.")
    
    @dev.command(hidden=True)
    @is_developer
    async def reload(self, context: Context, name: str):
        if name == self.__module__:
            await context.send(f"{context.author.mention}, you can't reload the extension '{name}'.")
            return
        if await self.__unload(context, name) and await self.__load(context, name):
            await context.send(f"{context.author.mention}, the extension '{name}' has been **reloaded**.")
    
    @dev.command(hidden=True)
    @is_developer
    async def unload(self, context: Context, name: str):
        if name == self.__module__:
            await context.send(f"{context.author.mention}, you can't unload the extension '{name}'.")
            return
        if await self.__unload(context, name):
            await context.send(f"{context.author.mention}, the extension '{name}' has been **unloaded**.")

    @dev.command(hidden=True)
    @is_developer
    async def log_level(self, context: Context, log_level: str):
        self.__log.log_level = LogLevel.parse(log_level)
        await context.send(f"{context.author.mention}, the log level has been changed.")
    
    # This is an extremely dangerous piece of code because it evaluates ANY expression.
    # Use it at your own risk only and never in a production environment!
    @dev.command(hidden=True)
    @is_developer
    async def eval(self, context: Context, *, expression: str):
        if not self.__configurator.get("General", "IsDebug", False):
            self.__log.warning(f"[Dev] [Development] The user '{context.author.id}' attempted to evaluate arbitrary code, but debug mode is disabled.")
            return
        self.__log.info(f"Evaluating the following expression:\n{expression}")
        eval(expression)
    
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
        await context.send(f"{context.author.mention}, failed to load the extension '{name}', because {reason}.")
        return False
    
    async def __unload(self, context: Context, name: str):
        try:
            self.__bot.unload_extension(name)
            return True
        except ExtensionNotLoaded:
            await context.send(f"{context.author.mention}, the extension '{name}' isn't loaded.")
        return False

    @unload.error
    @load.error
    @reload.error
    async def on_error(self, context: Context, error):
        if isinstance(error, AuthorizationError):
            self.__log.warning(f"[Dev] [Development] The unauthorized user with the identifier '{context.author.id}' tried to execute '{context.command}'.")
            return
        await context.author.send(f"Your command '{context.command}' generated the following error: {error}")
        await context.send(f"{context.author.mention}, an error has occurred while executing your command. A DM has been sent to you with the details.")

def setup(bot: Bot):
    bot.add_cog(Development(bot))