from .. import CommandRuleManagerInterface
from ..enums import RuleState
from ..exceptions import InvalidCommandError
from ..models import CommandRule
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.models import Choice, CommandResponse, Option, ServerChatInteractionContext
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.utils import get_channel_id
from holobot.sdk.ioc.decorators import injectable
from typing import Optional

@injectable(CommandInterface)
class SetCommandRuleCommand(CommandBase):
    def __init__(self, rule_manager: CommandRuleManagerInterface) -> None:
        super().__init__("setrule")
        self.__command_rule_manager: CommandRuleManagerInterface = rule_manager
        self.group_name = "admin"
        self.subgroup_name = "commands"
        self.description = "Adds a new or modifies an existing rule for one or more commands."
        self.options = [
            Option("state", "Whether to allow or forbid commands.", choices=[
                Choice("Allow", "Allow"),
                Choice("Forbid", "Forbid")
            ]),
            Option("group", "An entire command group, such as \"admin\".", is_mandatory=False),
            Option("subgroup", "An entire subgroup, such as \"commands\".", is_mandatory=False),
            Option("command", "A command inside a command group, such as \"roll\".", is_mandatory=False),
            Option("channel", "The link of the applicable channel.", is_mandatory=False)
        ]
        self.required_permissions = Permission.ADMINISTRATOR
        
    async def execute(self, context: ServerChatInteractionContext, state: str, group: Optional[str] = None, subgroup: Optional[str] = None, command: Optional[str] = None, channel: Optional[str] = None) -> CommandResponse:
        if context.server_id is None:
            return CommandResponse(
                action=ReplyAction(content="Command rules can be defined in servers only.")
            )

        channel_id = None
        if channel is not None:
            channel_id = get_channel_id(channel)
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
            return CommandResponse(
                action=ReplyAction(content=f"Your rule has been set: {rule.textify()}")
            )
        except InvalidCommandError:
            return CommandResponse(
                action=ReplyAction(content="This command doesn't exist or rules cannot be set for it.")
            )
