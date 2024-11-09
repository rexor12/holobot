from uuid import uuid4

import hikari

from holobot.discord.actions import IActionProcessor
from holobot.discord.sdk.events import CommandProcessedEvent
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows.interactables import Command
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.discord.sdk.workflows.models import (
    DirectMessageInteractionContext, ServerChatInteractionContext
)
from holobot.discord.sdk.workflows.rules import IWorkflowExecutionRule
from holobot.discord.workflows import (
    IInteractionProcessor, InteractionProcessorBase, IWorkflowRegistry
)
from holobot.discord.workflows.models import InteractionDescriptor
from holobot.sdk.diagnostics import IExecutionContextFactory
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.reactive import IListener

@injectable(IInteractionProcessor[hikari.CommandInteraction])
class CommandProcessor(InteractionProcessorBase[hikari.CommandInteraction, Command]):
    def __init__(
        self,
        action_processor: IActionProcessor,
        event_listeners: tuple[IListener[CommandProcessedEvent], ...],
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
        interaction: hikari.CommandInteraction
    ) -> InteractionDescriptor[Command]:
        group_name = None
        subgroup_name = None
        command_name = interaction.command_name
        arguments = {}
        options: list[hikari.CommandInteractionOption] = (
            list(interaction.options) if interaction.options else []
        )
        while options:
            option = options.pop(0)
            match option.type:
                case hikari.OptionType.SUB_COMMAND_GROUP:
                    group_name = interaction.command_name
                    subgroup_name = option.name
                    options = list(option.options) if option.options else []
                case hikari.OptionType.SUB_COMMAND:
                    group_name = group_name or interaction.command_name
                    command_name = option.name
                    options = list(option.options) if option.options else []
                case _:
                    arguments[option.name] = InteractionProcessorBase._resolve_argument(
                        option.value,
                        option.type
                    )

        invocation_target = self.__workflow_registry.get_command(
            group_name,
            subgroup_name,
            command_name
        )

        return InteractionDescriptor(
            workflow=invocation_target[0] if invocation_target else None,
            interactable=invocation_target[1] if invocation_target else None,
            arguments=arguments,
            initiator_id=interaction.user.id,
            bound_user_id=interaction.user.id,
            context=self.__get_interaction_context(interaction)
        )

    async def _on_interaction_processed(
        self,
        interaction: hikari.CommandInteraction,
        descriptor: InteractionDescriptor[Command],
        response: InteractionResponse
    ) -> None:
        if not self.__event_listeners:
            return

        # At this point the interactable cannot be None.
        assert descriptor.interactable

        event = CommandProcessedEvent(
            interactable=descriptor.interactable,
            server_id=interaction.guild_id,
            channel_id=interaction.channel_id,
            user_id=interaction.user.id,
            arguments=descriptor.arguments,
            response=response
        )
        for event_listener in self.__event_listeners:
            await event_listener.on_event(event)

    def __get_interaction_context(
        self,
        interaction: hikari.CommandInteraction
    ) -> InteractionContext:
        if interaction.guild_id:
            return ServerChatInteractionContext(
                request_id=uuid4(),
                author_id=interaction.user.id,
                author_name=interaction.user.username,
                author_nickname=interaction.member.nickname if interaction.member else None,
                message=None,
                server_id=interaction.guild_id,
                server_name=guild.name if (guild := interaction.get_guild()) else "Unknown Server",
                channel_id=interaction.channel_id
            )

        return DirectMessageInteractionContext(
            request_id=uuid4(),
            author_id=interaction.user.id,
            author_name=interaction.user.username,
            author_nickname=None,
            message=None,
            channel_id=interaction.channel_id
        )
