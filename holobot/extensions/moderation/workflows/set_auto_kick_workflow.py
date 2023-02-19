from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.exceptions import ArgumentOutOfRangeError
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from ..managers import IWarnManager
from .interactables.decorators import moderation_command
from .responses import AutoKickToggledResponse

@injectable(IWorkflow)
class SetAutoKickWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        warn_manager: IWarnManager
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__warn_manager = warn_manager

    @moderation_command(
        description="Enables automatic kicking of people with warn strikes.",
        name="setkick",
        group_name="moderation",
        subgroup_name="auto",
        options=(
            Option("warn_count", "The number of warns after which a user is automatically kicked.", OptionType.INTEGER),
        ),
        required_permissions=Permission.ADMINISTRATOR
    )
    async def set_auto_kick(
        self,
        context: InteractionContext,
        warn_count: int
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(
                content=self.__i18n_provider.get("interactions.server_only_interaction_error")
            )

        try:
            await self.__warn_manager.enable_auto_kick(context.server_id, warn_count)
        except ArgumentOutOfRangeError as error:
            return InteractionResponse(
                action=ReplyAction(
                    content=self.__i18n_provider.get(
                        "extensions.moderation.warn_count_out_of_range_error",
                        { "min": error.lower_bound, "max": error.upper_bound }
                    )
                )
            )

        return AutoKickToggledResponse(
            author_id=context.author_id,
            is_enabled=True,
            warn_count=warn_count,
            action=ReplyAction(
                content=self.__i18n_provider.get(
                    "extensions.moderation.set_auto_kick_workflow.autokick_configured",
                    { "warns": warn_count }
                )
            )
        )
