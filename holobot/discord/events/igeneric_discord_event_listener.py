from typing import Protocol

import hikari

from holobot.discord.bot import Bot

class IGenericDiscordEventListener(Protocol):
    @property
    def event_type(self) -> type:
        ...

    async def process(self, bot: Bot, event: hikari.Event) -> None:
        ...
