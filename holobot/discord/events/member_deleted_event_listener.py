from typing import Any, Type

import hikari

from holobot.discord.bot import Bot
from holobot.discord.sdk.events import ServerMemberLeftEvent
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.reactive import IListener
from .discord_event_listener_base import DiscordEventListenerBase
from .igeneric_discord_event_listener import IGenericDiscordEventListener

_EVENT_TYPE = hikari.MemberDeleteEvent

@injectable(IGenericDiscordEventListener)
class MemberDeletedEventListener(DiscordEventListenerBase[_EVENT_TYPE]):
    def __init__(
        self,
        listeners: tuple[IListener[ServerMemberLeftEvent], ...]
    ) -> None:
        super().__init__()
        self.__listeners = sorted(listeners, key=lambda i: i.priority)

    @property
    def event_type(self) -> Type[Any]:
        return _EVENT_TYPE

    async def on_event(self, bot: Bot, event: _EVENT_TYPE) -> None:
        local_event = ServerMemberLeftEvent(
            server_id=str(event.guild_id),
            user_id=str(event.user_id)
        )

        for listener in self.__listeners:
            await listener.on_event(local_event)
