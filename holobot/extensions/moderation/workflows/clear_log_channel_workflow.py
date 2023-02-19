from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from ..managers import ILogManager
from .interactables.decorators import moderation_command
from .responses import LogChannelToggledResponse

@injectable(IWorkflow)
class ClearLogChannelWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        log_manager: ILogManager
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__log_manager = log_manager

    @moderation_command(
        description="Disables the logging of moderation actions.",
        name="clearchannel",
        group_name="moderation",
        subgroup_name="logs",
        required_permissions=Permission.ADMINISTRATOR
    )
    async def disable_channel_logging(
        self,
        context: InteractionContext
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(
                content=self.__i18n_provider.get("interactions.server_only_interaction_error")
            )

        await self.__log_manager.set_log_channel(context.server_id, None)
        return LogChannelToggledResponse(
            author_id=context.author_id,
            action=ReplyAction(
                content=self.__i18n_provider.get(
                    "extensions.moderation.clear_log_channel_workflow.logs_disabled"
                )
            )
        )
