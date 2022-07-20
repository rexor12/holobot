from .interactables.decorators import moderation_command
from ..managers import IWarnManager
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import textify_timedelta

@injectable(IWorkflow)
class ViewWarnDecayWorkflow(WorkflowBase):
    def __init__(self, warn_manager: IWarnManager) -> None:
        super().__init__()
        self.__warn_manager: IWarnManager = warn_manager

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
        return InteractionResponse(action=ReplyAction(
            content=f"The warn decay is set to {textify_timedelta(decay_threshold)}."
                    if decay_threshold else "There is no warn decay set for the server."
        ))