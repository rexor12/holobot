from .interactables.decorators import moderation_command
from .responses import LogChannelToggledResponse
from ..managers import ILogManager
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class ClearLogChannelWorkflow(WorkflowBase):
    def __init__(self, log_manager: ILogManager) -> None:
        super().__init__()
        self.__log_manager: ILogManager = log_manager
    
    @moderation_command(
        description="Disables the logging of moderation actions.",
        name="clearchannel",
        group_name="moderation",
        subgroup_name="logs",
        required_permissions=Permission.ADMINISTRATOR
    )
    async def disable_channel_logging(
        self,
        context: ServerChatInteractionContext
    ) -> InteractionResponse:
        await self.__log_manager.set_log_channel(context.server_id, None)
        return LogChannelToggledResponse(
            author_id=context.author_id,
            action=ReplyAction(content="Moderation actions won't be logged anymore.")
        )
