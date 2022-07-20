from .. import CommandRegistryInterface, CommandRuleManagerInterface
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.utils import get_channel_id_or_default
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable
from typing import Optional

@injectable(IWorkflow)
class TestCommandWorkflow(WorkflowBase):
    def __init__(
        self,
        command_registry: CommandRegistryInterface,
        rule_manager: CommandRuleManagerInterface
    ) -> None:
        super().__init__(required_permissions=Permission.ADMINISTRATOR)
        self.__command_registry: CommandRegistryInterface = command_registry
        self.__command_rule_manager: CommandRuleManagerInterface = rule_manager

    @command(
        description="Checks if a command can be used in the current or the specified channel.",
        name="test",
        group_name="admin",
        subgroup_name="commands",
        options=(
            Option("command", "The specific command, such as \"roll\"."),
            Option("group", "The command group, such as \"admin\".", is_mandatory=False),
            Option("subgroup", "The command subgroup, such as \"commands\".", is_mandatory=False),
            Option("channel", "The channel to test.", is_mandatory=False)
        )
    )
    async def test_command(
        self,
        context: ServerChatInteractionContext,
        command: str,
        group: Optional[str] = None,
        subgroup: Optional[str] = None,
        channel: Optional[str] = None
    ) -> InteractionResponse:
        if context.server_id is None:
            return InteractionResponse(
                action=ReplyAction(content="Command rules can be defined in servers only.")
            )

        if not self.__command_registry.command_exists(command, group, subgroup):
            return InteractionResponse(
                action=ReplyAction(content="The command you specified doesn't exist. Did you make a typo?")
            )

        channel_id = get_channel_id_or_default(channel, context.channel_id) if channel is not None else context.channel_id
        can_execute = await self.__command_rule_manager.can_execute(context.server_id, channel_id, group, subgroup, command)
        disabled_text = "" if can_execute else " NOT"
        return InteractionResponse(
            action=ReplyAction(content=f"The command CAN{disabled_text} be executed in <#{channel_id}>.")
        )
