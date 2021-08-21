from discord_slash.context import MenuContext
from holobot.discord.sdk.context_menus import IMenuItem
from typing import Any

class IMenuItemProcessor:
    async def process(self, menu_item: IMenuItem, context: MenuContext, **kwargs: Any) -> None:
        raise NotImplementedError
