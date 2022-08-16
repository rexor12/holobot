from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from .. import CommandRuleManagerInterface

@injectable(IWorkflow)
class RemoveAllCommandRulesWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        rule_manager: CommandRuleManagerInterface
    ) -> None:
        super().__init__(required_permissions=Permission.ADMINISTRATOR)
        self.__command_rule_manager: CommandRuleManagerInterface = rule_manager
        self.__i18n_provider = i18n_provider

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
                action=ReplyAction(content=self.__i18n_provider.get(
                    "extensions.admin.remove_all_command_rules_workflow.no_rules_removed"
                ))
            )

        await self.__command_rule_manager.remove_rules_by_server(context.server_id)
        return InteractionResponse(
            action=ReplyAction(content=self.__i18n_provider.get(
                "extensions.admin.remove_all_command_rules_workflow.all_rules_removed"
            ))
        )
