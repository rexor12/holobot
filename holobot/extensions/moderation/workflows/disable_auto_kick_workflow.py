from .interactables.decorators import moderation_command
from .responses import AutoKickToggledResponse
from ..managers import IWarnManager
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class DisableAutoKickWorkflow(WorkflowBase):
    def __init__(self, warn_manager: IWarnManager) -> None:
        super().__init__()
        self.__warn_manager: IWarnManager = warn_manager

    @moderation_command(
        description="Disables automatic user kicking.",
        name="disablekick",
        group_name="moderation",
        subgroup_name="auto",
        required_permissions=Permission.ADMINISTRATOR
    )
    async def disable_auto_kick(
        self,
        context: ServerChatInteractionContext
    ) -> InteractionResponse:
        await self.__warn_manager.disable_auto_kick(context.server_id)
        return AutoKickToggledResponse(
            author_id=context.author_id,
            action=ReplyAction(content="Users won't be kicked automatically anymore.")
        )