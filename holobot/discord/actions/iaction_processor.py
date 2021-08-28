from discord_slash.context import MenuContext, SlashContext
from holobot.discord.sdk.actions import ActionBase
from typing import Union

class IActionProcessor:
    async def process(self, context: Union[MenuContext, SlashContext], action: ActionBase) -> None:
        raise NotImplementedError
