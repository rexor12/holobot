from typing import Tuple
from uuid import uuid4

from hikari import CommandInteraction, CommandType

from .imenu_item_processor import IMenuItemProcessor
from holobot.discord.actions import IActionProcessor
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows.interactables import MenuItem
from holobot.discord.sdk.workflows.models import ServerMessageInteractionContext, ServerUserInteractionContext
from holobot.discord.sdk.workflows.rules import IWorkflowExecutionRule
from holobot.discord.workflows import InteractionProcessorBase, IWorkflowRegistry
from holobot.discord.workflows.models import InteractionDescriptor
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface

@injectable(IMenuItemProcessor)
class MenuItemProcessor(InteractionProcessorBase[CommandInteraction, MenuItem], IMenuItemProcessor):
    def __init__(
        self,
        action_processor: IActionProcessor,
        log: LogInterface,
        workflow_execution_rules: Tuple[IWorkflowExecutionRule, ...],
        workflow_registry: IWorkflowRegistry
    ) -> None:
        super().__init__(action_processor, log, workflow_execution_rules)
        self.__workflow_registry = workflow_registry

    def _get_interactable_descriptor(
        self,
        interaction: CommandInteraction
    ) -> InteractionDescriptor[MenuItem]:
        invocation_target = self.__workflow_registry.get_menu_item(interaction.command_name)
        return InteractionDescriptor(
            workflow=invocation_target[0] if invocation_target else None,
            interactable=invocation_target[1] if invocation_target else None
        )

    def _get_interaction_context(
        self,
        interaction: CommandInteraction
    ) -> InteractionContext:
        # TODO Support non-server specific commands.
        if not interaction.guild_id:
            raise NotImplementedError("Non-server specific commands are not supported.")

        if interaction.command_type == CommandType.MESSAGE:
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
        elif interaction.command_type == CommandType.USER:
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
