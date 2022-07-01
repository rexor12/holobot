from ..bot import Bot
from abc import ABCMeta, abstractmethod
from hikari.api.special_endpoints import ContextMenuCommandBuilder
from holobot.discord.sdk.context_menus import IMenuItem
from typing import Optional, Sequence

class IMenuItemRegistry(metaclass=ABCMeta):
    @abstractmethod
    def get_menu_item(self, name: str) -> Optional[IMenuItem]:
        ...

    @abstractmethod
    def get_command_builders(self, bot: Bot) -> Sequence[ContextMenuCommandBuilder]:
        ...
