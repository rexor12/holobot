from .bot import Bot
from .bot_service_interface import BotServiceInterface
from ..messaging import Messaging
from ..sdk import ExtensionProviderInterface
from asyncio.tasks import Task
from discord import Intents
from discord_slash import SlashCommand, SlashContext
from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.ioc import ServiceCollectionInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from holobot.sdk.logging.enums import LogLevel
from typing import Optional, Tuple

import asyncio

DEFAULT_BOT_PREFIX = "h!"
DEBUG_MODE_BOT_PREFIX = "h#"

intents = Intents(
    guilds=True,
    members=True,
    emojis=True,
    voice_states=True,
    guild_messages=True,
    guild_reactions=True
)

@injectable(BotServiceInterface)
class BotService(BotServiceInterface):
    def __init__(self, services: ServiceCollectionInterface) -> None:
        super().__init__()
        self.__configurator: ConfiguratorInterface = services.get(ConfiguratorInterface)
        self.__extension_providers: Tuple[ExtensionProviderInterface, ...] = services.get_all(ExtensionProviderInterface)
        self.__log: LogInterface = services.get(LogInterface).with_name("Discord", "BotService")
        self.__bot: Bot = self.__initialize_bot(services)
        self.__slash: SlashCommand = SlashCommand(self.__bot, sync_commands=True, sync_on_cog_reload=True)
        self.__bot_task: Optional[Task] = None
        # See the reference for a note about what this is.
        Messaging.bot = self.__bot

    async def start(self) -> None:
        if self.__bot_task is not None:
            raise InvalidOperationError("The bot is running already.")

        if not (discord_token := self.__configurator.get("General", "DiscordToken", "")):
            raise ValueError("The Discord token is not configured.")
        
        self.__log.info("[BotService] Loading extensions...")
        extension_count = 0
        for extension_provider in self.__extension_providers:
            for package in extension_provider.get_packages():
                self.__log.debug(f"[BotService] Loading extension... {{ Package = {package} }}")
                self.__bot.load_extension(package)
                extension_count += 1
                self.__log.debug(f"[BotService] Loaded extension. {{ Package = {package} }}")
        self.__log.info(f"[BotService] Successfully loaded extensions. {{ Count = {extension_count} }}")
        
        self.__bot_task = asyncio.get_event_loop().create_task(self.__bot.start(discord_token))
    
    async def stop(self) -> None:
        if self.__bot_task is None:
            return
        
        await self.__bot.logout()
        await self.__bot_task
        self.__bot_task = None

    async def send_dm(self, user_id: str, message: str) -> None:
        if not (user := self.__bot.get_user_by_id(int(user_id))):
            self.__log.warning(f"[BotService] Inexistent user. {{ UserId = {user_id}, Operation = DM }}")
            return
        await user.send(message)
    
    def __initialize_bot(self, services: ServiceCollectionInterface) -> Bot:
        bot = Bot(
            services,
            # TODO Guild-specific custom prefix.
            command_prefix = DEFAULT_BOT_PREFIX if not self.__configurator.get("General", "IsDebug", False) else DEBUG_MODE_BOT_PREFIX,
            case_insensitive = True,
            intents = intents,
            loop = asyncio.get_event_loop()
        )

        bot.add_listener(self.__on_slash_command_error, "on_slash_command_error")

        return bot
	
    async def __on_slash_command_error(self, context: SlashContext, exception: Exception) -> None:
        self.__log.write(LogLevel.DEBUG, "[BotService] An error has occurred while processing a slash command.", exception)
