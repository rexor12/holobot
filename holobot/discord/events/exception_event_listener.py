import hikari

from holobot.discord.bot import Bot
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from .discord_event_listener_base import DiscordEventListenerBase
from .igeneric_discord_event_listener import IGenericDiscordEventListener

_EVENT_TYPE = hikari.ExceptionEvent

@injectable(IGenericDiscordEventListener)
class ExceptionEventListener(DiscordEventListenerBase[_EVENT_TYPE]):
    def __init__(
        self,
        logger_factory: ILoggerFactory,
    ) -> None:
        super().__init__()
        self.__logger = logger_factory.create(ExceptionEventListener)

    @property
    def event_type(self) -> type:
        return _EVENT_TYPE

    async def on_event(self, bot: Bot, event: _EVENT_TYPE) -> None:
        self.__logger.error(
            "An event handler has raised an error.",
            event.exception,
            exception_type=type(event.exception).__name__,
            failed_event=event.failed_event
        )
