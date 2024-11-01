import hikari
from hikari.api.special_endpoints import CommandBuilder

from holobot.discord.bot import Bot
from holobot.discord.workflows import IWorkflowRegistry
from holobot.sdk.diagnostics import DebuggerInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.utils import get_or_add
from .discord_event_listener_base import DiscordEventListenerBase
from .igeneric_discord_event_listener import IGenericDiscordEventListener

_EVENT_TYPE = hikari.StartingEvent

@injectable(IGenericDiscordEventListener)
class StartingEventListener(DiscordEventListenerBase[_EVENT_TYPE]):
    def __init__(
        self,
        debugger: DebuggerInterface,
        logger_factory: ILoggerFactory,
        workflow_registry: IWorkflowRegistry
    ) -> None:
        super().__init__()
        self.__debugger = debugger
        self.__logger = logger_factory.create(StartingEventListener)
        self.__workflow_registry = workflow_registry

    @property
    def event_type(self) -> type:
        return _EVENT_TYPE

    async def on_event(self, bot: Bot, event: _EVENT_TYPE) -> None:
        command_builders = await self.__get_command_builders(bot)
        await self.__register_commands(bot, command_builders)
        self.__logger.info("Registered all application commands")

    async def __get_command_builders(
        self,
        bot: Bot
    ) -> dict[str, list[CommandBuilder]]:
        builder_tree: dict[str, list[CommandBuilder]] = {}
        command_builders = await self.__workflow_registry.get_command_builders(bot)
        for server_id, builders in command_builders.items():
            cb = get_or_add(builder_tree, server_id, lambda _: list[CommandBuilder](), None)
            cb.extend(builders)

        menu_item_builders = await self.__workflow_registry.get_menu_item_builders(bot)
        for server_id, builders in menu_item_builders.items():
            cb = get_or_add(builder_tree, server_id, lambda _: list[CommandBuilder](), None)
            cb.extend(builders)

        return builder_tree

    async def __register_commands(
        self,
        bot: Bot,
        command_builders: dict[str, list[CommandBuilder]]
    ) -> None:
        application = await bot.rest.fetch_application()
        for server_id, builders in command_builders.items():
            try:
                await bot.rest.set_application_commands(
                    application=application.id,
                    commands=builders,
                    guild=int(server_id) if server_id != "" else hikari.UNDEFINED
                )
            except Exception as error:
                self.__logger.error(
                    "Failed to register some server-specific application commands",
                    error,
                    server_id=server_id
                )
