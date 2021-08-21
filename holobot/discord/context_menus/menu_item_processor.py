from .imenu_item_processor import IMenuItemProcessor
from discord_slash.context import MenuContext
from holobot.discord.sdk.context_menus import IMenuItem, IMenuItemExecutionRule, MenuItemResponse
from holobot.discord.sdk.events import MenuItemExecutedEvent
from holobot.discord.sdk.utils import reply
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from holobot.sdk.reactive import ListenerInterface
from typing import Any, Tuple

import time

@injectable(IMenuItemProcessor)
class MenuItemProcessor(IMenuItemProcessor):
    def __init__(self,
        log: LogInterface,
        menu_item_executed_event_handlers: Tuple[ListenerInterface[MenuItemExecutedEvent], ...],
        menu_item_execution_rules: Tuple[IMenuItemExecutionRule, ...]) -> None:
        super().__init__()
        self.__log: LogInterface = log.with_name("Discord", "MenuItemProcessor")
        self.__menu_item_executed_event_handlers: Tuple[ListenerInterface[MenuItemExecutedEvent], ...] = menu_item_executed_event_handlers
        self.__menu_item_execution_rules: Tuple[IMenuItemExecutionRule, ...] = menu_item_execution_rules

    async def process(self, menu_item: IMenuItem, context: MenuContext, **kwargs: Any) -> None:
        self.__log.trace(f"Executing menu item... {{ Type= {type(menu_item)} }}")
        start_time = time.perf_counter()
        await context.defer()
        for rule in self.__menu_item_execution_rules:
            if await rule.should_halt(menu_item, context):
                self.__log.debug(f"Menu item has been halted. {{ Type = {type(menu_item)} }}")
                await reply(context, "You're not allowed to use this command here.")
                return

        response = await menu_item.execute(context, **kwargs)
        await self.__on_menu_item_executed(menu_item, context, response)

        elapsed_time = int((time.perf_counter() - start_time) * 1000)
        self.__log.debug(f"Executed menu item. {{ Type = {type(menu_item)}, Elapsed = {elapsed_time} }}")

    async def __on_menu_item_executed(self, menu_item: IMenuItem, context: MenuContext, response: MenuItemResponse) -> None:
        event = MenuItemExecutedEvent(
            menu_item_type=type(menu_item),
            server_id=str(context.guild_id),
            user_id=str(context.author_id),
            response=response
        )
        for handler in self.__menu_item_executed_event_handlers:
            await handler.on_event(event)
