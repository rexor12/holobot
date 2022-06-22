from .imenu_item_registry import IMenuItemRegistry
from ..bot import Bot
from hikari.api.special_endpoints import ContextMenuCommandBuilder
from holobot.discord.sdk.context_menus import IMenuItem, IUserMenuItem
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from typing import Dict, Optional, Sequence, Tuple

import hikari

@injectable(IMenuItemRegistry)
class MenuItemRegistry(IMenuItemRegistry):
    def __init__(self,
        log: LogInterface,
        user_menu_items: Tuple[IMenuItem, ...]) -> None:
        super().__init__()
        self.__log: LogInterface = log.with_name("Discord", "ContextMenuItemRegistry")
        self.__user_menu_items: Dict[str, IMenuItem] = {
            menu_item.name: menu_item
            for menu_item in user_menu_items
        }

    def get_menu_item(self, name: str) -> Optional[IMenuItem]:
        return self.__user_menu_items.get(name)

    def get_command_builders(self, bot: Bot) -> Sequence[ContextMenuCommandBuilder]:
        self.__log.info("Registering user menu items...")
        context_menu_item_builders = []
        for menu_item in sorted(self.__user_menu_items.values()):
            if isinstance(menu_item, IUserMenuItem):
                context_menu_item_builders.append(self.__get_user_menu_item_builder(bot, menu_item))
            else: raise TypeError(f"Unexpected menu item type '{type(menu_item)}'.")
        self.__log.info(f"Successfully registered user menu items. {{ Count = {len(self.__user_menu_items)} }}")
        return context_menu_item_builders

    def __get_user_menu_item_builder(self, bot: Bot, menu_item: IUserMenuItem) -> ContextMenuCommandBuilder:
        builder = bot.rest.context_menu_command_builder(
            type=hikari.CommandType.USER, # TODO Support others.
            name=menu_item.name
        )
        self.__log.debug(f"Registered user menu item. {{ Type = {menu_item.name} }}")
        return builder
