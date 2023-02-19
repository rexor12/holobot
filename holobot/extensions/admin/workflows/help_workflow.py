from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class HelpWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider
    ) -> None:
        super().__init__(required_permissions=Permission.ADMINISTRATOR)
        self.__i18n_provider = i18n_provider

    @command(
        description="A brief explanation of how the rules are applied to the commands.",
        name="help",
        group_name="admin",
        subgroup_name="commands"
    )
    async def show_help(
        self,
        context: InteractionContext
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(
                content=self.__i18n_provider.get("interactions.server_only_interaction_error")
            )

        return InteractionResponse(
            action=ReplyAction(content=self.__i18n_provider.get(
                "extensions.admin.help_workflow.explanation"
            ))
        )
