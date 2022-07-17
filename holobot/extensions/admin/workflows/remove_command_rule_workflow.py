from .. import CommandRuleManagerInterface
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class RemoveCommandRuleWorkflow(WorkflowBase):
    def __init__(self, rule_manager: CommandRuleManagerInterface) -> None:
        super().__init__(required_permissions=Permission.ADMINISTRATOR)
        self.__command_rule_manager: CommandRuleManagerInterface = rule_manager

    @command(
        description="Removes the specified rule.",
        name="removerule",
        group_name="admin",
        subgroup_name="commands",
        options=(
            Option("identifier", "The identifier of the rule.", OptionType.INTEGER),
        )
    )
    async def remove_command_rule(
        self,
        context: ServerChatInteractionContext,
        identifier: int
    ) -> InteractionResponse:
        await self.__command_rule_manager.remove_rule(identifier)
        return InteractionResponse(
            action=ReplyAction(content="The rule has been removed.")
        )
