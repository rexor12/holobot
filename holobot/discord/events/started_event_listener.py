from typing import Any, Type

import hikari

from holobot.discord.bot import Bot
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.system import IEnvironment
from .discord_event_listener_base import DiscordEventListenerBase
from .igeneric_discord_event_listener import IGenericDiscordEventListener

_EVENT_TYPE = hikari.StartedEvent

@injectable(IGenericDiscordEventListener)
class StartedEventListener(DiscordEventListenerBase[_EVENT_TYPE]):
    def __init__(
        self,
        environment: IEnvironment
    ) -> None:
        super().__init__()
        self.__environment = environment

    @property
    def event_type(self) -> Type[Any]:
        return _EVENT_TYPE

    async def on_event(self, bot: Bot, event: _EVENT_TYPE) -> None:
        await bot.update_presence(
            status=hikari.Status.ONLINE,
            activity=hikari.Activity(
                name=f"v{self.__environment.version}",
                type=hikari.ActivityType.PLAYING
            )
        )
