from typing import Tuple
from uuid import uuid4

from hikari import CommandInteraction, OptionType

from holobot.discord.actions import IActionProcessor
from holobot.discord.sdk.events import CommandProcessedEvent
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows.interactables import Command
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.discord.sdk.workflows.rules import IWorkflowExecutionRule
from holobot.discord.workflows import IInteractionProcessor, InteractionProcessorBase, IWorkflowRegistry
from holobot.discord.workflows.models import InteractionDescriptor
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.diagnostics import IExecutionContextFactory
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.reactive import IListener

@injectable(IInteractionProcessor[CommandInteraction])
class CommandProcessor(InteractionProcessorBase[CommandInteraction, Command]):
    def __init__(
        self,
        action_processor: IActionProcessor,
        event_listeners: Tuple[IListener[CommandProcessedEvent], ...],
        log: ILoggerFactory,
        measurement_context_factory: IExecutionContextFactory,
        workflow_execution_rules: Tuple[IWorkflowExecutionRule, ...],
        workflow_registry: IWorkflowRegistry
    ) -> None:
        super().__init__(action_processor, log, measurement_context_factory, workflow_execution_rules)
        self.__event_listeners = sorted(event_listeners, key=lambda i: i.priority)
        self.__workflow_registry = workflow_registry

    def _get_interactable_descriptor(
        self,
        interaction: CommandInteraction
    ) -> InteractionDescriptor[Command]:
        group_name = None
        subgroup_name = None
        command_name = interaction.command_name
        arguments = {}
        options = list(interaction.options) if interaction.options else []
        while options:
            option = options.pop(0)
            if option.type == OptionType.SUB_COMMAND_GROUP:
                group_name = interaction.command_name
                subgroup_name = option.name
                options = list(option.options) if option.options else []
            elif option.type == OptionType.SUB_COMMAND:
                group_name = group_name or interaction.command_name
                command_name = option.name
                options = list(option.options) if option.options else []
            else: arguments[option.name] = option.value

        invocation_target = self.__workflow_registry.get_command(
            group_name,
            subgroup_name,
            command_name
        )

        return InteractionDescriptor(
            workflow=invocation_target[0] if invocation_target else None,
            interactable=invocation_target[1] if invocation_target else None,
            arguments=arguments,
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

        return ServerChatInteractionContext(
            request_id=uuid4(),
            author_id=str(interaction.user.id),
            author_name=interaction.user.username,
            author_nickname=interaction.member.nickname if interaction.member else None,
            server_id=str(interaction.guild_id),
            server_name=guild.name if (guild := interaction.get_guild()) else "Unknown Server",
            channel_id=str(interaction.channel_id)
        )

    async def _on_interaction_processed(
        self,
        interaction: CommandInteraction,
        interactable: Command,
        response: InteractionResponse
    ) -> None:
        if not self.__event_listeners:
            return

        event = CommandProcessedEvent(
            command_type=type(interactable),
            server_id=str(interaction.guild_id),
            user_id=str(interaction.user.id),
            command=interactable.name,
            group=interactable.group_name,
            subgroup=interactable.subgroup_name,
            response=response
        )
        for event_listener in self.__event_listeners:
            await event_listener.on_event(event)
