from discord_slash.context import ComponentContext, MenuContext, SlashContext
from holobot.discord.sdk.actions import ActionBase
from typing import Union

class IActionProcessor:
    async def process(self, context: Union[ComponentContext, MenuContext, SlashContext], action: ActionBase) -> None:
        raise NotImplementedError
