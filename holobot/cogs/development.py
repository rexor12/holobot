from discord.ext.commands import Context
from discord.ext.commands.cog import Cog
from discord.ext.commands.core import group
from discord.ext.commands.errors import ExtensionAlreadyLoaded, ExtensionFailed, ExtensionNotFound, ExtensionNotLoaded, NoEntryPointError
from holobot.bot import Bot
from holobot.cogs.utils.is_developer import is_developer
from holobot.exceptions.authorization_error import AuthorizationError
from holobot.security.global_credential_manager_interface import GlobalCredentialManagerInterface

class Development(Cog, name="Development"):
    def __init__(self, bot: Bot):
        super().__init__()
        self.__bot = bot
        self.__credential_manager = bot.service_collection.get(GlobalCredentialManagerInterface)

    @group(hidden=True)
    async def cogs(self, context: Context):
        if context.invoked_subcommand is None:
            await context.send(f"{context.author.mention}, you have to specify a sub-command!", delete_after=3)
    
    @cogs.command(hidden=True)
    @is_developer
    async def load(self, context: Context, name: str):
        if name == self.__module__:
            await context.send(f"{context.author.mention}, you can't load the extension '{name}'.")
            return
        if await self.__load(context, name):
            await context.send(f"{context.author.mention}, the extension '{name}' has been **loaded**.")
    
    @cogs.command(hidden=True)
    @is_developer
    async def reload(self, context: Context, name: str):
        if name == self.__module__:
            await context.send(f"{context.author.mention}, you can't reload the extension '{name}'.")
            return
        if await self.__unload(context, name) and await self.__load(context, name):
            await context.send(f"{context.author.mention}, the extension '{name}' has been **reloaded**.")
    
    @cogs.command(hidden=True)
    @is_developer
    async def unload(self, context: Context, name: str):
        if name == self.__module__:
            await context.send(f"{context.author.mention}, you can't unload the extension '{name}'.")
            return
        if await self.__unload(context, name):
            await context.send(f"{context.author.mention}, the extension '{name}' has been **unloaded**.")
    
    # This is an extremely dangerous piece of code because it evaluates ANY expression.
    # Use it at your own risk only and never in a production environment!
    @cogs.command(hidden=True)
    @is_developer
    async def eval(self, context: Context, *, expression: str):
        if not self.__credential_manager.get("is_debug", False, bool):
            print(f"[Cogs] [Development] The user '{context.author.id}' attempted to evaluate arbitrary code, but debug mode is disabled.")
            return
        print(f"Evaluating the following expression:\n{expression}")
        eval(expression)
    
    async def __load(self, context: Context, name: str) -> bool:
        reason: str = None
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
            print(f"An extension has failed while being loaded.\n{error}")
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
            print(f"[Cogs] [Development] The unauthorized user with the identifier '{context.author.id}' tried to execute '{context.command}'.")
            return
        await context.author.send(f"Your command '{context.command}' generated the following error: {error}")
        await context.send(f"{context.author.mention}, an error has occurred while executing your command. A DM has been sent to you with the details.")

def setup(bot: Bot):
    bot.add_cog(Development(bot))