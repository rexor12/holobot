from uuid import uuid4

import hikari

from holobot.discord.actions import IActionProcessor
from holobot.discord.sdk.events import ComponentProcessedEvent
from holobot.discord.sdk.models import InteractionContext, Message
from holobot.discord.sdk.workflows.interactables import Component
from holobot.discord.sdk.workflows.interactables.components import ComponentStateBase
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.discord.sdk.workflows.models import (
    DirectMessageInteractionContext, ServerChatInteractionContext
)
from holobot.discord.sdk.workflows.rules import IWorkflowExecutionRule
from holobot.discord.transformers.embed import to_model
from holobot.discord.utils.interaction_utils import get_channel_and_thread_ids
from holobot.discord.workflows import (
    IInteractionProcessor, InteractionProcessorBase, IWorkflowRegistry
)
from holobot.discord.workflows.models import InteractionDescriptor
from holobot.discord.workflows.transformers import IComponentTransformer
from holobot.sdk.diagnostics import IExecutionContextFactory
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.reactive import IListener

@injectable(IInteractionProcessor[hikari.ComponentInteraction])
class ComponentProcessor(InteractionProcessorBase[hikari.ComponentInteraction, Component]):
    def __init__(
        self,
        action_processor: IActionProcessor,
        component_transformer: IComponentTransformer,
        event_listeners: tuple[IListener[ComponentProcessedEvent], ...],
        i18n_provider: II18nProvider,
        log: ILoggerFactory,
        measurement_context_factory: IExecutionContextFactory,
        workflow_execution_rules: tuple[IWorkflowExecutionRule, ...],
        workflow_registry: IWorkflowRegistry
    ) -> None:
        super().__init__(action_processor, i18n_provider, log, measurement_context_factory, workflow_execution_rules)
        self.__component_transformer = component_transformer
        self.__event_listeners = sorted(event_listeners, key=lambda i: i.priority)
        self.__workflow_registry = workflow_registry

    def _get_interactable_descriptor(
        self,
        interaction: hikari.ComponentInteraction
    ) -> InteractionDescriptor[Component]:
        component_id, index = self.__component_transformer.get_component_id(interaction.custom_id)
        invocation_target = self.__workflow_registry.get_component(component_id)
        context = self.__get_interaction_context(
            interaction,
            {
                component_id: invocation_target[1].state_type
            } if invocation_target else {}
        )
        if not context.message:
            raise InvalidOperationError("The interaction context does not have a message reference.")

        state = context.message.get_component(component_id, index) if invocation_target else None

        return InteractionDescriptor(
            workflow=invocation_target[0] if invocation_target else None,
            interactable=invocation_target[1] if invocation_target else None,
            arguments={
                "state": state
            },
            initiator_id=interaction.user.id,
            bound_user_id=state.owner_id if state else interaction.user.id,
            context=context
        )

    async def _on_interaction_processed(
        self,
        interaction: hikari.ComponentInteraction,
        descriptor: InteractionDescriptor[Component],
        response: InteractionResponse
    ) -> None:
        if not self.__event_listeners:
            return

        # At this point the interactable cannot be None.
        assert descriptor.interactable

        event = ComponentProcessedEvent(
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
        interaction: hikari.ComponentInteraction,
        expected_target_types: dict[str, type[ComponentStateBase]]
    ) -> InteractionContext:
        channel_id, thread_id = get_channel_and_thread_ids(interaction)

        if interaction.guild_id:
            return ServerChatInteractionContext(
                request_id=uuid4(),
                author_id=interaction.user.id,
                author_name=interaction.user.username,
                author_nickname=interaction.member.nickname if interaction.member else None,
                message=self.__create_message(interaction, expected_target_types),
                server_id=interaction.guild_id,
                server_name=guild.name if (guild := interaction.get_guild()) else "Unknown Server",
                channel_id=channel_id,
                thread_id=thread_id
            )

        return DirectMessageInteractionContext(
            request_id=uuid4(),
            author_id=interaction.user.id,
            author_name=interaction.user.username,
            author_nickname=None,
            message=self.__create_message(interaction, expected_target_types),
            channel_id=channel_id
        )

    def __create_message(
        self,
        interaction: hikari.ComponentInteraction,
        expected_target_types: dict[str, type[ComponentStateBase]]
    ) -> Message:
        channel_id, thread_id = get_channel_and_thread_ids(interaction)

        return Message(
            author_id=interaction.message.author.id,
            server_id=interaction.guild_id,
            channel_id=channel_id,
            thread_id=thread_id,
            message_id=interaction.message.id,
            content=interaction.message.content,
            embeds=tuple(map(to_model, interaction.message.embeds)),
            components=self.__component_transformer.create_control_states(
                interaction,
                expected_target_types
            )
        )
