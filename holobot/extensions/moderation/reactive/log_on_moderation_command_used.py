from ..commands import ModerationCommandBase
from holobot.discord.sdk.events import CommandExecutedEvent
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from holobot.sdk.reactive import ListenerInterface

@injectable(ListenerInterface[CommandExecutedEvent])
class LogOnModerationCommandUsed(ListenerInterface[CommandExecutedEvent]):
    def __init__(self, log: LogInterface) -> None:
        super().__init__()
        self.__log: LogInterface = log.with_name("Moderation", "LogOnModerationCommandUsed")

    async def on_event(self, event: CommandExecutedEvent):
        # TODO Save a log.
        if not issubclass(event.command_type, ModerationCommandBase):
            return

        self.__log.trace(f"A moderation command has been used. {{ Name = {event.command}, UserId = {event.user_id}, ServerId = {event.server_id} }}")
