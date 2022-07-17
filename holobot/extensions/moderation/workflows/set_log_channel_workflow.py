from .interactables.decorators import moderation_command
from .responses import LogChannelToggledResponse
from ..managers import ILogManager
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.utils import get_channel_id
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class SetLogChannelWorkflow(WorkflowBase):
    def __init__(self, log_manager: ILogManager) -> None:
        super().__init__()
        self.__log_manager: ILogManager = log_manager

    @moderation_command(
        description="Sets the channel in which moderation actions are logged.",
        name="setchannel",
        group_name="moderation",
        subgroup_name="logs",
        options=(
            Option("channel", "The mention of the channel to publish moderation logs in."),
        ),
        required_permissions=Permission.ADMINISTRATOR
    )
    async def set_log_channel(
        self,
        context: ServerChatInteractionContext,
        channel: str
    ) -> InteractionResponse:
        channel_id = get_channel_id(channel.strip())
        if not channel_id:
            return InteractionResponse(
                action=ReplyAction(content="You must mention a channel correctly.")
            )

        await self.__log_manager.set_log_channel(context.server_id, channel_id)
        return LogChannelToggledResponse(
            author_id=context.author_id,
            is_enabled=True,
            channel_id=channel_id,
            action=ReplyAction(content=f"Moderation actions will be logged in {channel}. Make sure I have the required permissions to send messages there.")
        )
