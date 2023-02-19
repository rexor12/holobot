from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from ..managers import IWarnManager
from .interactables.decorators import moderation_command
from .responses import AutoKickToggledResponse

@injectable(IWorkflow)
class DisableAutoKickWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        warn_manager: IWarnManager
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__warn_manager = warn_manager

    @moderation_command(
        description="Disables automatic user kicking.",
        name="disablekick",
        group_name="moderation",
        subgroup_name="auto",
        required_permissions=Permission.ADMINISTRATOR
    )
    async def disable_auto_kick(
        self,
        context: InteractionContext
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(
                content=self.__i18n_provider.get("interactions.server_only_interaction_error")
            )

        await self.__warn_manager.disable_auto_kick(context.server_id)
        return AutoKickToggledResponse(
            author_id=context.author_id,
            action=ReplyAction(
                content=self.__i18n_provider.get(
                    "extensions.moderation.disable_auto_kick_workflow.auto_kick_disabled"
                )
            )
        )
