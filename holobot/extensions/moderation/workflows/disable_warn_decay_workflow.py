from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from ..managers import IWarnManager
from .interactables.decorators import moderation_command
from .responses import WarnDecayToggledResponse

@injectable(IWorkflow)
class DisableWarnDecayWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        warn_manager: IWarnManager
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__warn_manager = warn_manager

    @moderation_command(
        description="Disables automatic warn strike removal.",
        name="disabledecay",
        group_name="moderation",
        subgroup_name="warns",
        required_permissions=Permission.ADMINISTRATOR
    )
    async def disable_warn_decay(
        self,
        context: ServerChatInteractionContext
    ) -> InteractionResponse:
        await self.__warn_manager.set_warn_decay(context.server_id, None)
        return WarnDecayToggledResponse(
            author_id=context.author_id,
            action=ReplyAction(
                content=self.__i18n_provider.get(
                    "extensions.moderation.disable_warn_decay_workflow.auto_warn_disabled"
                )
            )
        )
