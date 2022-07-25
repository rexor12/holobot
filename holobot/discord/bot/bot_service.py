from asyncio.tasks import Task
from typing import List, Optional

import asyncio
import hikari

from hikari import CommandInteraction, ComponentInteraction
from hikari.api.special_endpoints import CommandBuilder

from .bot_accessor import BotAccessor
from .bot import Bot
from .bot_service_interface import BotServiceInterface
from holobot.discord.workflows import IInteractionProcessor, IWorkflowRegistry
from holobot.discord.workflows.processors import IMenuItemProcessor
from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.diagnostics import DebuggerInterface
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory

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
        command_processor: IInteractionProcessor[CommandInteraction],
        component_processor: IInteractionProcessor[ComponentInteraction],
        logger_factory: ILoggerFactory,
        menu_item_processor: IMenuItemProcessor,
        workflow_registry: IWorkflowRegistry
    ) -> None:
        super().__init__()
        self.__debugger: DebuggerInterface = debugger
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

    async def send_dm(self, user_id: str, message: str) -> None:
        if not (user := self.__bot.get_user_by_id(int(user_id))):
            self.__log.warning(f"Inexistent user. {{ UserId = {user_id}, Operation = DM }}")
            return
        await user.send(message)

    def __initialize_bot(self, configurator: ConfiguratorInterface) -> Bot:
        if not (discord_token := configurator.get("General", "DiscordToken", "")):
            raise ValueError("The Discord token is not configured.")

        bot = Bot(
            discord_token,
            intents = REQUIRED_INTENTS
        )

        async def on_bot_starting(event: hikari.StartingEvent) -> None:
            await self.__on_bot_starting(bot, event)

        bot.subscribe(hikari.StartingEvent, on_bot_starting)
        bot.subscribe(hikari.ExceptionEvent, self.__on_error_event)
        bot.subscribe(hikari.InteractionCreateEvent, self.__on_interaction_created)

        return bot

    async def __on_bot_starting(self, bot: Bot, _: hikari.StartingEvent) -> None:
        application = await bot.rest.fetch_application()
        command_builders: List[CommandBuilder] = []
        command_builders.extend(self.__workflow_registry.get_command_builders(bot))
        command_builders.extend(self.__workflow_registry.get_menu_item_builders(bot))

        await bot.rest.set_application_commands(
            application=application.id,
            commands=command_builders,
            guild=self.__developer_server_id if self.__debugger.is_debug_mode_enabled() else hikari.UNDEFINED
        )
        self.__log.info("The bot has just started.")

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
            "An error has occurred while processing a slash command. ",
            event.exception,
            exception_type=type(event.exception).__name__,
            failed_event=event.failed_event
        )
