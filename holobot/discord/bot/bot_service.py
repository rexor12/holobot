import asyncio
from asyncio.tasks import Task
from collections.abc import Sequence

import hikari

from holobot.discord.events import IGenericDiscordEventListener
from holobot.sdk.configs import IConfigurator
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import get_or_add
from . import bot_accessor
from .bot import Bot
from .bot_service_interface import BotServiceInterface

REQUIRED_INTENTS = (
    hikari.Intents.ALL_DMS
    | hikari.Intents.ALL_GUILDS
    | hikari.Intents.ALL_MESSAGE_REACTIONS
    | hikari.Intents.ALL_MESSAGES
)

@injectable(BotServiceInterface)
class BotService(BotServiceInterface):
    def __init__(
        self,
        configurator: IConfigurator,
        discord_event_listeners: tuple[IGenericDiscordEventListener, ...]
    ) -> None:
        super().__init__()
        self.__discord_event_listeners = discord_event_listeners
        self.__bot: Bot = self.__initialize_bot(configurator)
        self.__bot_task: Task | None = None
        # See the reference for a note about what this is.
        bot_accessor._bot = self.__bot

    async def start(self) -> None:
        if self.__bot_task is not None:
            raise InvalidOperationError("The bot is running already.")

        self.__bot_task = asyncio.get_event_loop().create_task(self.__bot.start())

    async def stop(self) -> None:
        if self.__bot_task is None:
            return

        await self.__bot.close()
        await self.__bot_task
        self.__bot_task = None

    def __initialize_bot(self, configurator: IConfigurator) -> Bot:
        if not (discord_token := configurator.get("General", "DiscordToken", "")):
            raise ValueError("The Discord token is not configured.")

        bot = Bot(
            discord_token,
            intents = REQUIRED_INTENTS
        )

        event_listeners: dict[type[hikari.Event], list[IGenericDiscordEventListener]] = {}
        for listener in self.__discord_event_listeners:
            listeners = get_or_add(event_listeners, listener.event_type, lambda _: [], None)
            listeners.append(listener)

        def process_event_wrapper(b: Bot, l: Sequence[IGenericDiscordEventListener]):
            async def process_event(e: hikari.Event) -> None:
                await self.__process_event(b, l, e)
            return process_event

        for event_type, listeners in event_listeners.items():
            bot.subscribe(event_type, process_event_wrapper(bot, listeners))

        return bot

    async def __process_event(
        self,
        bot: Bot,
        listeners: Sequence[IGenericDiscordEventListener],
        event: hikari.Event
    ) -> None:
        for listener in listeners:
            await listener.process(bot, event)
