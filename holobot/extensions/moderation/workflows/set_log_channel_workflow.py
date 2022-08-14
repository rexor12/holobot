from .interactables.decorators import moderation_command
from .responses import LogChannelToggledResponse
from ..managers import ILogManager
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.utils import get_channel_id
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class SetLogChannelWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        log_manager: ILogManager
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__log_manager = log_manager

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
                action=ReplyAction(content=self.__i18n_provider.get("channel_not_found_error"))
            )

        await self.__log_manager.set_log_channel(context.server_id, channel_id)
        return LogChannelToggledResponse(
            author_id=context.author_id,
            is_enabled=True,
            channel_id=channel_id,
            action=ReplyAction(
                content=self.__i18n_provider.get(
                    "extensions.moderation.set_log_channel_workflow.modlog_configured",
                    { "channel_id": channel_id }
                )
            )
        )
