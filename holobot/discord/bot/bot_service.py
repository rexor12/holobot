from asyncio.tasks import Task
from typing import Dict, List, Optional, Sequence, Tuple, Type

import asyncio
import hikari

from hikari import CommandInteraction, ComponentInteraction
from hikari.api.special_endpoints import CommandBuilder

from .bot_accessor import BotAccessor
from .bot import Bot
from .bot_service_interface import BotServiceInterface
from holobot.discord.events import IGenericDiscordEventListener
from holobot.discord.workflows import IInteractionProcessor, IWorkflowRegistry
from holobot.discord.workflows.processors import IMenuItemProcessor
from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.diagnostics import DebuggerInterface
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.system import IEnvironment
from holobot.sdk.utils import get_or_add

DEFAULT_BOT_PREFIX = "h!"
DEBUG_MODE_BOT_PREFIX = "h#"

REQUIRED_INTENTS = (
    hikari.Intents.ALL_DMS
    | hikari.Intents.ALL_GUILDS
    | hikari.Intents.ALL_MESSAGE_REACTIONS
    | hikari.Intents.ALL_MESSAGES
)

@injectable(BotServiceInterface)
class BotService(BotServiceInterface):
    def __init__(self,
        configurator: ConfiguratorInterface,
        debugger: DebuggerInterface,
        discord_event_listeners: Tuple[IGenericDiscordEventListener, ...],
        environment: IEnvironment,
        command_processor: IInteractionProcessor[CommandInteraction],
        component_processor: IInteractionProcessor[ComponentInteraction],
        logger_factory: ILoggerFactory,
        menu_item_processor: IMenuItemProcessor,
        workflow_registry: IWorkflowRegistry
    ) -> None:
        super().__init__()
        self.__debugger = debugger
        self.__discord_event_listeners = discord_event_listeners
        self.__environment = environment
        self.__command_processor = command_processor
        self.__component_processor = component_processor
        self.__log = logger_factory.create(BotService)
        self.__menu_item_processor = menu_item_processor
        self.__workflow_registry = workflow_registry
        self.__developer_server_id: int = configurator.get("Development", "DevelopmentServerId", 0)
        self.__bot: Bot = self.__initialize_bot(configurator)
        self.__bot_task: Optional[Task] = None
        # See the reference for a note about what this is.
        BotAccessor._bot = self.__bot

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

    def __initialize_bot(self, configurator: ConfiguratorInterface) -> Bot:
        if not (discord_token := configurator.get("General", "DiscordToken", "")):
            raise ValueError("The Discord token is not configured.")

        bot = Bot(
            discord_token,
            intents = REQUIRED_INTENTS
        )

        event_listeners: Dict[Type[hikari.Event], List[IGenericDiscordEventListener]] = {}
        for listener in self.__discord_event_listeners:
            listeners = get_or_add(event_listeners, listener.event_type, lambda _: [], None)
            listeners.append(listener)

        async def on_bot_starting(event: hikari.StartingEvent) -> None:
            await self.__on_bot_starting(bot, event)

        async def on_bot_started(event: hikari.StartedEvent) -> None:
            await self.__on_bot_started(bot, event)

        def process_event_wrapper(b: Bot, l: Sequence[IGenericDiscordEventListener]):
            async def process_event(e: hikari.Event) -> None:
                await self.__process_event(b, l, e)
            return process_event

        # TODO Transform these into event listeners.
        bot.subscribe(hikari.StartingEvent, on_bot_starting)
        bot.subscribe(hikari.StartedEvent, on_bot_started)
        bot.subscribe(hikari.ExceptionEvent, self.__on_error_event)
        bot.subscribe(hikari.InteractionCreateEvent, self.__on_interaction_created)

        for event_type, listeners in event_listeners.items():
            bot.subscribe(event_type, process_event_wrapper(bot, listeners))

        return bot

    async def __on_bot_starting(self, bot: Bot, _: hikari.StartingEvent) -> None:
        application = await bot.rest.fetch_application()
        command_builders: Dict[str, List[CommandBuilder]] = {}
        for server_id, builders in self.__workflow_registry.get_command_builders(bot).items():
            cb = get_or_add(command_builders, server_id, lambda _: list[CommandBuilder](), None)
            cb.extend(builders)
        for server_id, builders in self.__workflow_registry.get_menu_item_builders(bot).items():
            cb = get_or_add(command_builders, server_id, lambda _: list[CommandBuilder](), None)
            cb.extend(builders)

        if self.__debugger.is_debug_mode_enabled():
            if str(self.__developer_server_id) in command_builders:
                cb = get_or_add(command_builders, "", lambda _: list[CommandBuilder](), None)
                cb.extend(command_builders.pop(str(self.__developer_server_id)))

        for server_id, builders in command_builders.items():
            await bot.rest.set_application_commands(
                application=application.id,
                commands=builders,
                guild=int(server_id) if server_id != ""
                      else self.__developer_server_id if self.__debugger.is_debug_mode_enabled()
                      else hikari.UNDEFINED
            )

        self.__log.info("The bot has just started")

    async def __on_bot_started(self, bot: Bot, _: hikari.StartedEvent) -> None:
        await bot.update_presence(
            status=hikari.Status.ONLINE,
            activity=hikari.Activity(
                name=f"v{self.__environment.version}",
                type=hikari.ActivityType.PLAYING
            )
        )

    async def __on_interaction_created(self, event: hikari.InteractionCreateEvent) -> None:
        if isinstance(event.interaction, hikari.CommandInteraction):
            if event.interaction.command_type == hikari.CommandType.SLASH:
                await self.__command_processor.process(event.interaction)
            elif event.interaction.command_type in (hikari.CommandType.USER, hikari.CommandType.MESSAGE):
                await self.__menu_item_processor.process(event.interaction)
        elif isinstance(event.interaction, hikari.ComponentInteraction):
            await self.__component_processor.process(event.interaction)

    async def __on_error_event(self, event: hikari.ExceptionEvent) -> None:
        self.__log.error(
            "An event handler has raised an error.",
            event.exception,
            exception_type=type(event.exception).__name__,
            failed_event=event.failed_event
        )

    async def __process_event(
        self,
        bot: Bot,
        listeners: Sequence[IGenericDiscordEventListener],
        event: hikari.Event
    ) -> None:
        for listener in listeners:
            await listener.process(bot, event)
