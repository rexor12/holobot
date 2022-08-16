from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import textify_timedelta
from ..managers import IWarnManager
from .interactables.decorators import moderation_command

@injectable(IWorkflow)
class ViewWarnDecayWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        warn_manager: IWarnManager
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__warn_manager = warn_manager

    @moderation_command(
        description="Displays the currently set warn decay.",
        name="viewdecay",
        group_name="moderation",
        subgroup_name="warns",
        required_permissions=Permission.ADMINISTRATOR
    )
    async def view_warn_decay(
        self,
        context: ServerChatInteractionContext
    ) -> InteractionResponse:
        decay_threshold = await self.__warn_manager.get_warn_decay(context.server_id)
        response_i18n = (
            "extensions.moderation.view_warn_decay_workflow.decay_enabled"
            if decay_threshold
            else "extensions.moderation.view_warn_decay_workflow.decay_disabled"
        )

        return InteractionResponse(action=ReplyAction(
            content=self.__i18n_provider.get(
                response_i18n,
                {
                    "time": textify_timedelta(decay_threshold)
                }
            )
        ))
