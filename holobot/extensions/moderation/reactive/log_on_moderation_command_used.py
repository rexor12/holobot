from ..commands import ModerationCommandBase
from .events import CommandUsedEvent
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from holobot.sdk.reactive import ListenerInterface

@injectable(ListenerInterface[CommandUsedEvent])
class LogOnModerationCommandUsed(ListenerInterface[CommandUsedEvent]):
    def __init__(self, log: LogInterface) -> None:
        super().__init__()
        self.__log: LogInterface = log.with_name("Moderation", "LogOnModerationCommandUsed")

    async def on_event(self, event: CommandUsedEvent):
        # TODO Save a log.
        if not isinstance(event.command, ModerationCommandBase):
            return
        self.__log.trace(f"A moderation command has been used. {{ Name = {event.command.name}, UserId = {event.user_id}, ServerId = {event.server_id} }}")
