from abc import ABCMeta, abstractmethod
from typing import Any, Generic, Type

import hikari

from .idiscord_event_listener import IDiscordEventListener, TEvent
from holobot.discord.bot import Bot

class DiscordEventListenerBase(
    Generic[TEvent],
    IDiscordEventListener[TEvent],
    metaclass=ABCMeta
):
    # Unfortunately, this needs to be abstract because
    # Python 3.10 doesn't support returning TEvent here.
    @property
    @abstractmethod
    def event_type(self) -> Type[Any]:
        ...

    def process(self, bot: Bot, event: hikari.Event):
        # Ignoring type here because isinstance() doesn't support TypeVars.
        return self.on_event(bot, event) # type: ignore

    @abstractmethod
    async def on_event(self, bot: Bot, event: TEvent) -> None:
        ...
