import hikari
from hikari.api.special_endpoints import CommandBuilder

from holobot.discord.bot import Bot
from holobot.discord.workflows import IWorkflowRegistry
from holobot.sdk.configs import ConfiguratorInterface
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
        configurator: ConfiguratorInterface,
        debugger: DebuggerInterface,
        logger_factory: ILoggerFactory,
        workflow_registry: IWorkflowRegistry
    ) -> None:
        super().__init__()
        self.__debugger = debugger
        self.__developer_server_id: int = configurator.get("Development", "DevelopmentServerId", 0)
        self.__logger = logger_factory.create(StartingEventListener)
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

        self.__logger.info("Registered all application commands")
