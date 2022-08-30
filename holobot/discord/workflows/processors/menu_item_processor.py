from uuid import uuid4

from hikari import CommandInteraction, CommandType

from holobot.discord.actions import IActionProcessor
from holobot.discord.sdk.events import MenuItemProcessedEvent
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows.interactables import MenuItem
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.discord.sdk.workflows.models import (
    ServerMessageInteractionContext, ServerUserInteractionContext
)
from holobot.discord.sdk.workflows.rules import IWorkflowExecutionRule
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
            initiator_id=str(interaction.user.id),
            bound_user_id=str(interaction.user.id)
        )

    def _get_interaction_context(
        self,
        interaction: CommandInteraction
    ) -> InteractionContext:
        # TODO Support non-server specific commands.
        if not interaction.guild_id:
            raise NotImplementedError("Non-server specific commands are not supported.")

        if interaction.command_type is CommandType.MESSAGE:
            return ServerMessageInteractionContext(
                request_id=uuid4(),
                author_id=str(interaction.user.id),
                author_name=interaction.user.username,
                author_nickname=interaction.member.nickname if interaction.member else None,
                server_id=str(interaction.guild_id),
                server_name=guild.name if (guild := interaction.get_guild()) else None,
                channel_id=str(interaction.channel_id),
                target_message_id=str(interaction.target_id)
            )
        elif interaction.command_type is CommandType.USER:
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
        else: raise ValueError(f"The command type '{interaction.command_type}' is not supported.")

    async def _on_interaction_processed(
        self,
        interaction: CommandInteraction,
        interactable: MenuItem,
        response: InteractionResponse
    ) -> None:
        if not self.__event_listeners:
            return

        event = MenuItemProcessedEvent(
            menu_item_type=type(interactable),
            server_id=str(interaction.guild_id) if interaction.guild_id else None,
            user_id=str(interaction.user.id),
            response=response
        )
        for event_listener in self.__event_listeners:
            await event_listener.on_event(event)
