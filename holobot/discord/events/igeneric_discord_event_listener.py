from typing import Any, Protocol, Type

import hikari

from holobot.discord.bot import Bot

class IGenericDiscordEventListener(Protocol):
    @property
    def event_type(self) -> Type[Any]:
        ...

    async def process(self, bot: Bot, event: hikari.Event) -> None:
        ...
