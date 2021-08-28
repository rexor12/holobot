from discord_slash import SlashContext
from holobot.discord.sdk.commands import CommandInterface
from typing import Any

class ICommandProcessor:
    async def process(self, __command: CommandInterface, context: SlashContext, **kwargs: Any) -> None:
        raise NotImplementedError
