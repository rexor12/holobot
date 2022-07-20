from .. import CommandRuleManagerInterface
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class RemoveAllCommandRulesWorkflow(WorkflowBase):
    def __init__(self, rule_manager: CommandRuleManagerInterface) -> None:
        super().__init__(required_permissions=Permission.ADMINISTRATOR)
        self.__command_rule_manager: CommandRuleManagerInterface = rule_manager

    @command(
        description="Removes ALL command rules specified for this server.",
        name="removeall",
        group_name="admin",
        subgroup_name="commands",
        options=(
            Option("confirmation", "Type \"confirm\" if you are sure about this."),
        )
    )
    async def execute(self, context: ServerChatInteractionContext, confirmation: str) -> InteractionResponse:
        if confirmation != "confirm":
            return InteractionResponse(
                action=ReplyAction(content="No rules have been removed. You must confirm your intention correctly.")
            )

        await self.__command_rule_manager.remove_rules_by_server(context.server_id)
        return InteractionResponse(
            action=ReplyAction(content="ALL rules specified for this server have been removed.")
        )
