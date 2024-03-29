from abc import ABCMeta, abstractmethod
from typing import Generic

import hikari

from holobot.discord.bot import Bot
from .idiscord_event_listener import IDiscordEventListener, TEvent

class DiscordEventListenerBase(
    Generic[TEvent],
    IDiscordEventListener[TEvent],
    metaclass=ABCMeta
):
    # Unfortunately, this needs to be abstract because
    # Python 3.10 doesn't support returning TEvent here.
    @property
    @abstractmethod
    def event_type(self) -> type:
        ...

    def process(self, bot: Bot, event: hikari.Event):
        # Ignoring type here because isinstance() doesn't support TypeVars.
        return self.on_event(bot, event) # type: ignore

    @abstractmethod
    async def on_event(self, bot: Bot, event: TEvent) -> None:
        ...
