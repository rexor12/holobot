from typing import cast
from uuid import uuid4

from hikari import CommandInteraction, CommandType

from holobot.discord.actions import IActionProcessor
from holobot.discord.sdk.events import MenuItemProcessedEvent
from holobot.discord.sdk.exceptions import InteractionContextNotSupportedError
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows.interactables import MenuItem
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.discord.sdk.workflows.models import (
    ServerMessageInteractionContext, ServerUserInteractionContext
)
from holobot.discord.sdk.workflows.rules import IWorkflowExecutionRule
from holobot.discord.utils.interaction_utils import get_channel_and_thread_ids
from holobot.discord.workflows import InteractionProcessorBase, IWorkflowRegistry
from holobot.discord.workflows.models import InteractionDescriptor
from holobot.sdk.diagnostics import IExecutionContextFactory
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.reactive import IListener
from .imenu_item_processor import IMenuItemProcessor

@injectable(IMenuItemProcessor)
class MenuItemProcessor(InteractionProcessorBase[CommandInteraction, MenuItem], IMenuItemProcessor):
    def __init__(
        self,
        action_processor: IActionProcessor,
        event_listeners: tuple[IListener[MenuItemProcessedEvent], ...],
        i18n_provider: II18nProvider,
        log: ILoggerFactory,
        measurement_context_factory: IExecutionContextFactory,
        workflow_execution_rules: tuple[IWorkflowExecutionRule, ...],
        workflow_registry: IWorkflowRegistry
    ) -> None:
        super().__init__(action_processor, i18n_provider, log, measurement_context_factory, workflow_execution_rules)
        self.__event_listeners = sorted(event_listeners, key=lambda i: i.priority)
        self.__workflow_registry = workflow_registry

    def _get_interactable_descriptor(
        self,
        interaction: CommandInteraction
    ) -> InteractionDescriptor[MenuItem]:
        invocation_target = self.__workflow_registry.get_menu_item(interaction.command_name)
        return InteractionDescriptor(
            workflow=invocation_target[0] if invocation_target else None,
            interactable=invocation_target[1] if invocation_target else None,
            initiator_id=interaction.user.id,
            bound_user_id=interaction.user.id,
            context=self.__get_interaction_context(interaction)
        )

    async def _on_interaction_processed(
        self,
        interaction: CommandInteraction,
        descriptor: InteractionDescriptor[MenuItem],
        response: InteractionResponse
    ) -> None:
        if not self.__event_listeners:
            return

        # At this point the interactable cannot be None.
        assert descriptor.interactable

        event = MenuItemProcessedEvent(
            interactable=descriptor.interactable,
            server_id=interaction.guild_id,
            channel_id=interaction.channel_id,
            user_id=interaction.user.id,
            response=response
        )
        for event_listener in self.__event_listeners:
            await event_listener.on_event(event)

    def __get_interaction_context(
        self,
        interaction: CommandInteraction
    ) -> InteractionContext:
        if not interaction.guild_id:
            raise InteractionContextNotSupportedError()

        channel_id, thread_id = get_channel_and_thread_ids(interaction)

        match interaction.command_type:
            case CommandType.MESSAGE:
                return ServerMessageInteractionContext(
                    request_id=uuid4(),
                    author_id=interaction.user.id,
                    author_name=interaction.user.username,
                    author_nickname=interaction.member.nickname if interaction.member else None,
                    message=None,
                    server_id=interaction.guild_id,
                    server_name=guild.name if (guild := interaction.get_guild()) else None,
                    channel_id=channel_id,
                    thread_id=thread_id,
                    target_message_id=cast(int, interaction.target_id)
                )
            case CommandType.USER:
                return ServerUserInteractionContext(
                    request_id=uuid4(),
                    author_id=interaction.user.id,
                    author_name=interaction.user.username,
                    author_nickname=interaction.member.nickname if interaction.member else None,
                    message=None,
                    server_id=interaction.guild_id,
                    server_name=guild.name if (guild := interaction.get_guild()) else None,
                    channel_id=channel_id,
                    thread_id=thread_id,
                    target_user_id=cast(int, interaction.target_id)
                )
            case _:
                raise InteractionContextNotSupportedError()
