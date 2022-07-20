from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class HelpWorkflow(WorkflowBase):
    def __init__(self) -> None:
        super().__init__(required_permissions=Permission.ADMINISTRATOR)

    @command(
        description="A brief explanation of how the rules are applied to the commands.",
        name="help",
        group_name="admin",
        subgroup_name="commands"
    )
    async def show_help(
        self,
        context: ServerChatInteractionContext
    ) -> InteractionResponse:
        return InteractionResponse(
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
