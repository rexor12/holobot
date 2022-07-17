from .. import CommandRuleManagerInterface
from ..enums import RuleState
from ..exceptions import InvalidCommandError
from ..models import CommandRule
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.utils import get_channel_id
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import Choice, InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable
from typing import Optional

@injectable(IWorkflow)
class SetCommandRuleWorkflow(WorkflowBase):
    def __init__(self, rule_manager: CommandRuleManagerInterface) -> None:
        super().__init__(required_permissions=Permission.ADMINISTRATOR)
        self.__command_rule_manager: CommandRuleManagerInterface = rule_manager

    @command(
        description="Adds a new or modifies an existing rule for one or more commands.",
        name="setrule",
        group_name="admin",
        subgroup_name="commands",
        options=(
            Option("state", "Whether to allow or forbid commands.", choices=(
                Choice("Allow", "Allow"),
                Choice("Forbid", "Forbid")
            )),
            Option("group", "An entire command group, such as \"admin\".", is_mandatory=False),
            Option("subgroup", "An entire subgroup, such as \"commands\".", is_mandatory=False),
            Option("command", "A command inside a command group, such as \"roll\".", is_mandatory=False),
            Option("channel", "The link of the applicable channel.", is_mandatory=False)
        )
    )
    async def set_command_rule(
        self,
        context: ServerChatInteractionContext,
        state: str,
        group: Optional[str] = None,
        subgroup: Optional[str] = None,
        command: Optional[str] = None,
        channel: Optional[str] = None
    ) -> InteractionResponse:
        if context.server_id is None:
            return InteractionResponse(
                action=ReplyAction(content="Command rules can be defined in servers only.")
            )

        channel_id = get_channel_id(channel) if channel is not None else None
        rule = CommandRule()
        rule.created_by = context.author_id
        rule.server_id = context.server_id
        rule.state = RuleState.parse(state)
        rule.group = group
        rule.subgroup = subgroup
        rule.command = command
        rule.channel_id = channel_id
        try:
            await self.__command_rule_manager.set_rule(rule)
            return InteractionResponse(
                action=ReplyAction(content=f"Your rule has been set: {rule.textify()}")
            )
        except InvalidCommandError:
            return InteractionResponse(
                action=ReplyAction(content="This command doesn't exist or rules cannot be set for it.")
            )
