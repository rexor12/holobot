from .bot import Bot
from asyncio.tasks import Task
from discord import Intents
from holobot.discord.sdk import ExtensionProviderInterface
from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.integration import IntegrationInterface
from holobot.sdk.ioc import ServiceCollectionInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from typing import List, Optional

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

@injectable(IntegrationInterface)
class Integration(IntegrationInterface):
    def __init__(self, services: ServiceCollectionInterface) -> None:
        super().__init__()
        self.__log: LogInterface = services.get(LogInterface)
        self.__configurator: ConfiguratorInterface = services.get(ConfiguratorInterface)
        self.__extension_providers: List[ExtensionProviderInterface] = services.get_all(ExtensionProviderInterface)
        self.__bot: Bot = self.__initialize_bot(services)
        self.__bot_task: Optional[Task] = None
        self.__log.info("[Integration] Initialized Discord integration.")

    async def start(self) -> None:
        self.__log.debug("[Integration] Starting Discord integration...")
        if self.__bot_task is not None:
            raise InvalidOperationError("The bot is running already.")

        if not (discord_token := self.__configurator.get("General", "DiscordToken", "")):
            raise ValueError("The Discord token is not configured.")
        
        self.__bot_task = asyncio.get_event_loop().create_task(self.__bot.start(discord_token))
        self.__log.info("[Integration] Discord integration started.")
    
    async def stop(self) -> None:
        self.__log.debug("[Integration] Stopping Discord integration...")
        if self.__bot_task is not None:
            await self.__bot.logout()
            await self.__bot_task
            self.__bot_task = None
        self.__log.info("[Integration] Discord integration stopped.")
    
    def __initialize_bot(self, services: ServiceCollectionInterface) -> Bot:
        bot = Bot(
            services,
            # TODO Guild-specific custom prefix.
            command_prefix = DEFAULT_BOT_PREFIX if not self.__configurator.get("General", "IsDebug", False) else DEBUG_MODE_BOT_PREFIX,
            case_insensitive = True,
            intents = intents,
            loop = asyncio.get_event_loop()
        )

        self.__log.info("[Integration] Loading extensions...")
        extension_count = 0
        for extension_provider in self.__extension_providers:
            for package in extension_provider.get_packages():
                self.__log.debug(f"[Integration] Loading extension... {{ Package = {package} }}")
                bot.load_extension(package)
                extension_count += 1
                self.__log.debug(f"[Integration] Loaded extension. {{ Package = {package} }}")
        # bot.load_extension("holobot.extensions.crypto.cogs.crypto")
        # bot.load_extension("holobot.extensions.dev.cogs.main")
        # bot.load_extension("holobot.extensions.hentai.cogs.main")
        # bot.load_extension("holobot.extensions.reminders.cogs.reminders")
        # bot.load_extension("holobot.extensions.todo_lists.cogs.main")
        self.__log.info(f"[Integration] Successfully loaded extensions. {{ Count = {extension_count} }}")

        return bot
