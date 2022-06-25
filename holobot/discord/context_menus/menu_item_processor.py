from .imenu_item_processor import IMenuItemProcessor
from .imenu_item_registry import IMenuItemRegistry
from ..actions import IActionProcessor
from hikari import CommandInteraction, ResponseType
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.context_menus import IMenuItem, IMenuItemExecutionRule
from holobot.discord.sdk.context_menus.models import MenuItemResponse, ServerUserInteractionContext
from holobot.discord.sdk.events import MenuItemExecutedEvent
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from holobot.sdk.reactive import ListenerInterface
from typing import Any, Dict, NamedTuple, Tuple
from uuid import uuid4

import time

class MenuItemDetails(NamedTuple):
    name: str
    arguments: Dict[str, Any]

@injectable(IMenuItemProcessor)
class MenuItemProcessor(IMenuItemProcessor):
    def __init__(self,
        action_processor: IActionProcessor,
        log: LogInterface,
        menu_item_executed_event_handlers: Tuple[ListenerInterface[MenuItemExecutedEvent], ...],
        menu_item_execution_rules: Tuple[IMenuItemExecutionRule, ...],
        menu_item_registry: IMenuItemRegistry
    ) -> None:
        super().__init__()
        self.__action_processor: IActionProcessor = action_processor
        self.__log: LogInterface = log.with_name("Discord", "MenuItemProcessor")
        self.__menu_item_executed_event_handlers: Tuple[ListenerInterface[MenuItemExecutedEvent], ...] = menu_item_executed_event_handlers
        self.__menu_item_execution_rules: Tuple[IMenuItemExecutionRule, ...] = menu_item_execution_rules
        self.__menu_item_registry: IMenuItemRegistry = menu_item_registry

    async def process(self, interaction: CommandInteraction) -> None:
        self.__log.trace(f"Executing menu item... {{ Name = {interaction.command_name} }}")
        start_time = time.perf_counter()
        await interaction.create_initial_response(response_type=ResponseType.DEFERRED_MESSAGE_CREATE)

        interaction_context = MenuItemProcessor.__get_context(interaction)
        details = MenuItemProcessor.__get_menu_item_details(interaction)
        if not (menu_item := self.__menu_item_registry.get_menu_item(details.name)):
            await self.__action_processor.process(interaction, ReplyAction(content="You've invoked an inexistent menu item."), DeferType.DEFER_MESSAGE_CREATION)
            return

        for rule in self.__menu_item_execution_rules:
            if await rule.should_halt(menu_item, interaction_context):
                self.__log.debug(f"Menu item has been halted. {{ Type = {type(menu_item).__name__}, Rule = {type(rule).__name__} }}")
                await self.__action_processor.process(interaction, ReplyAction(content="You're not allowed to use this command here."), DeferType.DEFER_MESSAGE_CREATION)
                return

            response = await menu_item.execute(interaction_context, **details.arguments)
            await self.__action_processor.process(interaction, response.action, DeferType.DEFER_MESSAGE_CREATION)
            await self.__on_menu_item_executed(menu_item, interaction, response)

        elapsed_time = int((time.perf_counter() - start_time) * 1000)
        self.__log.debug(f"Executed menu item. {{ Type = {type(menu_item)}, Elapsed = {elapsed_time} }}")

    @staticmethod
    def __get_context(interaction: CommandInteraction) -> ServerUserInteractionContext:
        return ServerUserInteractionContext(
            request_id=uuid4(),
            author_id=str(interaction.user.id),
            author_name=interaction.user.username,
            author_nickname=interaction.member.nickname if interaction.member else None,
            server_id=str(interaction.guild_id),
            server_name=guild.name if (guild := interaction.get_guild()) else None,
            channel_id=str(interaction.channel_id),
            target_user_id=str(interaction.target_id)
        )

    @staticmethod
    def __get_menu_item_details(interaction: CommandInteraction) -> MenuItemDetails:
        return MenuItemDetails(
            interaction.command_name,
            {
                option.name: option.value
                for option in (interaction.options or ())
            }
        )

    async def __on_menu_item_executed(self, menu_item: IMenuItem, interaction: CommandInteraction, response: MenuItemResponse) -> None:
        event = MenuItemExecutedEvent(
            menu_item_type=type(menu_item),
            server_id=str(interaction.guild_id) if interaction.guild_id else None,
            user_id=str(interaction.user.id),
            response=response
        )
        for handler in self.__menu_item_executed_event_handlers:
            await handler.on_event(event)
