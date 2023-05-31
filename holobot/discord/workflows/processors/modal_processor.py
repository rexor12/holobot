from uuid import uuid4

from hikari import ModalInteraction

from holobot.discord.actions import IActionProcessor
from holobot.discord.sdk.events import ModalProcessedEvent
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows.interactables import Modal
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.discord.sdk.workflows.models import (
    DirectMessageInteractionContext, ServerChatInteractionContext
)
from holobot.discord.sdk.workflows.rules import IWorkflowExecutionRule
from holobot.discord.workflows import (
    IInteractionProcessor, InteractionProcessorBase, IWorkflowRegistry
)
from holobot.discord.workflows.models import InteractionDescriptor
from holobot.discord.workflows.transformers import IComponentTransformer
from holobot.sdk.diagnostics import IExecutionContextFactory
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.reactive import IListener

@injectable(IInteractionProcessor[ModalInteraction])
class ModalProcessor(InteractionProcessorBase[ModalInteraction, Modal]):
    def __init__(
        self,
        action_processor: IActionProcessor,
        component_transformer: IComponentTransformer,
        event_listeners: tuple[IListener[ModalProcessedEvent], ...],
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
        interaction: ModalInteraction
    ) -> InteractionDescriptor[Modal]:
        modal_id = interaction.custom_id.split("~", 1)[0]
        invocation_target = self.__workflow_registry.get_modal(modal_id)
        state = self.__component_transformer.transform_modal_state(
            interaction
        ) if invocation_target else None

        return InteractionDescriptor(
            workflow=invocation_target[0] if invocation_target else None,
            interactable=invocation_target[1] if invocation_target else None,
            arguments={
                "state": state
            },
            initiator_id=str(interaction.user.id),
            bound_user_id=state.owner_id if state else str(interaction.user.id)
        )

    def _get_interaction_context(
        self,
        interaction: ModalInteraction
    ) -> InteractionContext:
        if interaction.guild_id:
            return ServerChatInteractionContext(
                request_id=uuid4(),
                author_id=str(interaction.user.id),
                author_name=interaction.user.username,
                author_nickname=interaction.member.nickname if interaction.member else None,
                server_id=str(interaction.guild_id),
                server_name=guild.name if (guild := interaction.get_guild()) else "Unknown Server",
                channel_id=str(interaction.channel_id)
            )

        return DirectMessageInteractionContext(
            request_id=uuid4(),
            author_id=str(interaction.user.id),
            author_name=interaction.user.username,
            author_nickname=None,
            channel_id=str(interaction.channel_id)
        )

    async def _on_interaction_processed(
        self,
        interaction: ModalInteraction,
        descriptor: InteractionDescriptor[Modal],
        response: InteractionResponse
    ) -> None:
        if not self.__event_listeners:
            return

        # At this point the interactable cannot be None.
        assert descriptor.interactable

        event = ModalProcessedEvent(
            interactable=descriptor.interactable,
            server_id=str(interaction.guild_id),
            channel_id=str(interaction.channel_id),
            user_id=str(interaction.user.id),
            response=response
        )
        for event_listener in self.__event_listeners:
            await event_listener.on_event(event)
