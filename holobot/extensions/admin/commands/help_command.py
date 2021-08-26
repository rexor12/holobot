from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, ServerChatInteractionContext
from holobot.discord.sdk.enums import Permission
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class HelpCommand(CommandBase):
    def __init__(self) -> None:
        super().__init__("help")
        self.group_name = "admin"
        self.subgroup_name = "commands"
        self.description = "A brief explanation of how the rules are applied to the commands."
        self.required_permissions = Permission.ADMINISTRATOR
        
    async def execute(self, context: ServerChatInteractionContext) -> CommandResponse:
        return CommandResponse(
            action=ReplyAction(content=(
                "Rules are logically separated by the following types:\n"
                "- **Global rules**: These rules apply to every command, regardless of group, sub-group or name.\n"
                "- **Group rules**: These rules apply to entire command groups, such as \"admin\".\n"
                "- **Sub-group rules**: These rules apply to a specific sub-group of a specific group, such as \"commands\".\n"
                "- **Command rules**: These rules apply to specific commands, such as \"help\".\n"
                "Each one of these groups may apply to all channels or a specific channel only.\n\n"
                "The rule precedence is as follows: _global rules > group rules > sub-group rules > command rules_."
                " Rules that apply to all channels are applied before those that apply to specific channels only.\n\n"
                "For example, to allow the execution of commands in a single channel only, you would need two rules:\n"
                "1. :no_entry: Forbid the execution of all commands in every channel.\n"
                "2. :white_check_mark: Allow the execution of all commands in a specific channel."
            ))
        )
