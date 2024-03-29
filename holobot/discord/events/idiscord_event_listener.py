from typing import Generic, Protocol, TypeVar

import hikari

from holobot.discord.bot import Bot
from .igeneric_discord_event_listener import IGenericDiscordEventListener

TEvent = TypeVar("TEvent", bound=hikari.Event, contravariant=True)

class IDiscordEventListener(Generic[TEvent], IGenericDiscordEventListener, Protocol):
    async def on_event(self, bot: Bot, event: TEvent) -> None:
        ...
