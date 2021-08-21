from typing import Tuple
from .imenu_item_processor import IMenuItemProcessor
from .imenu_item_registry import IMenuItemRegistry
from discord_slash import ContextMenuType, SlashCommand
from holobot.discord.sdk.context_menus import IMenuItem, IUserMenuItem
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface

@injectable(IMenuItemRegistry)
class MenuItemRegistry(IMenuItemRegistry):
    def __init__(self,
        log: LogInterface,
        menu_item_processor: IMenuItemProcessor,
        user_menu_items: Tuple[IMenuItem, ...]) -> None:
        super().__init__()
        self.__log: LogInterface = log.with_name("Discord", "ContextMenuItemRegistry")
        self.__menu_item_processor: IMenuItemProcessor = menu_item_processor
        self.__user_menu_items: Tuple[IMenuItem, ...] = tuple(sorted(user_menu_items))

    def register_menu_items(self, slash: SlashCommand) -> None:
        self.__log.info("Registering user menu items...")
        for menu_item in self.__user_menu_items:
            if isinstance(menu_item, IUserMenuItem):
                self.__register_user_menu_item(slash, menu_item)
            else: raise TypeError(f"Unexpected menu item type '{type(menu_item)}'.")
        self.__log.info(f"Successfully registered user menu items. {{ Count = {len(self.__user_menu_items)} }}")

    def __register_user_menu_item(self, slash: SlashCommand, menu_item: IUserMenuItem) -> None:
        slash.add_context_menu(
            lambda context, **kwargs: self.__menu_item_processor.process(menu_item, context, **kwargs),
            menu_item.name,
            ContextMenuType.USER
        )
        self.__log.debug(f"Registered user menu item. {{ Type = {menu_item.name} }}")
