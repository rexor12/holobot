from .imenu_item_processor import IMenuItemProcessor
from ..actions import IActionProcessor
from ..contexts import IContextManager
from discord_slash.context import MenuContext
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.context_menus import IMenuItem, IMenuItemExecutionRule
from holobot.discord.sdk.context_menus.models import MenuItemResponse, ServerUserInteractionContext
from holobot.discord.sdk.events import MenuItemExecutedEvent
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from holobot.sdk.reactive import ListenerInterface
from typing import Any, Tuple
from uuid import uuid4

import time

@injectable(IMenuItemProcessor)
class MenuItemProcessor(IMenuItemProcessor):
    def __init__(self,
        action_processor: IActionProcessor,
        context_manager: IContextManager,
        log: LogInterface,
        menu_item_executed_event_handlers: Tuple[ListenerInterface[MenuItemExecutedEvent], ...],
        menu_item_execution_rules: Tuple[IMenuItemExecutionRule, ...]) -> None:
        super().__init__()
        self.__action_processor: IActionProcessor = action_processor
        self.__context_manager: IContextManager = context_manager
        self.__log: LogInterface = log.with_name("Discord", "MenuItemProcessor")
        self.__menu_item_executed_event_handlers: Tuple[ListenerInterface[MenuItemExecutedEvent], ...] = menu_item_executed_event_handlers
        self.__menu_item_execution_rules: Tuple[IMenuItemExecutionRule, ...] = menu_item_execution_rules

    async def process(self, menu_item: IMenuItem, context: MenuContext, **kwargs: Any) -> None:
        # TODO Strip str type kwargs.
        self.__log.trace(f"Executing menu item... {{ Type= {type(menu_item)} }}")
        start_time = time.perf_counter()
        await context.defer()
        interaction_context = MenuItemProcessor.__transform_context(context)

        async with await self.__context_manager.register_context(interaction_context.request_id, context):
            for rule in self.__menu_item_execution_rules:
                if await rule.should_halt(menu_item, interaction_context):
                    self.__log.debug(f"Menu item has been halted. {{ Type = {type(menu_item)} }}")
                    await self.__action_processor.process(context, ReplyAction(content="You're not allowed to use this command here."))
                    return

            response = await menu_item.execute(interaction_context, **kwargs)
            await self.__action_processor.process(context, response.action)
            await self.__on_menu_item_executed(menu_item, context, response)

        elapsed_time = int((time.perf_counter() - start_time) * 1000)
        self.__log.debug(f"Executed menu item. {{ Type = {type(menu_item)}, Elapsed = {elapsed_time} }}")

    @staticmethod
    def __transform_context(context: MenuContext) -> ServerUserInteractionContext:
        return ServerUserInteractionContext(
            request_id=uuid4(),
            author_id=str(context.author_id),
            author_name=context.author.name,
            server_id=str(context.guild_id),
            server_name=context.guild.name,
            channel_id=str(context.channel_id),
            target_user_id=str(context.target_author.id)
        )

    async def __on_menu_item_executed(self, menu_item: IMenuItem, context: MenuContext, response: MenuItemResponse) -> None:
        event = MenuItemExecutedEvent(
            menu_item_type=type(menu_item),
            server_id=str(context.guild_id),
            user_id=str(context.author_id),
            response=response
        )
        for handler in self.__menu_item_executed_event_handlers:
            await handler.on_event(event)
