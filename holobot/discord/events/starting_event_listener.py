import hikari
from hikari.api.special_endpoints import CommandBuilder

from holobot.discord import DiscordOptions
from holobot.discord.bot import Bot
from holobot.discord.workflows import IWorkflowRegistry
from holobot.sdk.configs import IOptions
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
        options: IOptions[DiscordOptions],
        workflow_registry: IWorkflowRegistry
    ) -> None:
        super().__init__()
        self.__debugger = debugger
        self.__logger = logger_factory.create(StartingEventListener)
        self.__options = options
        self.__workflow_registry = workflow_registry

    @property
    def event_type(self) -> type:
        return _EVENT_TYPE

    async def on_event(self, bot: Bot, event: _EVENT_TYPE) -> None:
        application = await bot.rest.fetch_application()
        command_builders: dict[str, list[CommandBuilder]] = {}
        for server_id, builders in self.__workflow_registry.get_command_builders(bot).items():
            cb = get_or_add(command_builders, server_id, lambda _: list[CommandBuilder](), None)
            cb.extend(builders)
        for server_id, builders in self.__workflow_registry.get_menu_item_builders(bot).items():
            cb = get_or_add(command_builders, server_id, lambda _: list[CommandBuilder](), None)
            cb.extend(builders)

        is_debug_mode_enabled = self.__debugger.is_debug_mode_enabled()
        development_server_id = self.__options.value.DevelopmentServerId
        if is_debug_mode_enabled:
            if str(development_server_id) in command_builders:
                cb = get_or_add(command_builders, "", lambda _: list[CommandBuilder](), None)
                cb.extend(command_builders.pop(str(development_server_id)))
            self.__logger.debug(
                "Skipping registration of some server-specific commands due to debug mode"
            )

        for server_id, builders in command_builders.items():
            if (
                is_debug_mode_enabled
                and server_id != ""
                and server_id not in self.__options.value.DebugServerIds
            ):
                self.__logger.debug(
                    "Skipping registration of non-debug server specific commands",
                    server_id=server_id
                )
                continue

            try:
                await bot.rest.set_application_commands(
                    application=application.id,
                    commands=builders,
                    guild=int(server_id) if server_id != ""
                        else development_server_id if is_debug_mode_enabled
                        else hikari.UNDEFINED
                )
            except Exception as error:
                self.__logger.error(
                    "Failed to register some server-specific application commands",
                    error,
                    server_id=server_id
                )

        self.__logger.info("Registered all application commands")
