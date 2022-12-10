from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.chrono import InvalidInputError, parse_interval
from holobot.sdk.exceptions import ArgumentOutOfRangeError
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import textify_timedelta
from ..managers import IWarnManager
from .interactables.decorators import moderation_command
from .responses import WarnDecayToggledResponse

@injectable(IWorkflow)
class SetWarnDecayWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        warn_manager: IWarnManager
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__warn_manager = warn_manager

    @moderation_command(
        description="Enables automatic warn strike removal.",
        name="setdecay",
        group_name="moderation",
        subgroup_name="warns",
        options=(
            Option("duration", "The duration after which a warn strike is removed from a user. Eg. 1d, 1h or 30m."),
        ),
        required_permissions=Permission.ADMINISTRATOR
    )
    async def set_warn_decay(
        self,
        context: ServerChatInteractionContext,
        duration: str
    ) -> InteractionResponse:
        try:
            decay_threshold = parse_interval(duration.strip())
        except (ArgumentOutOfRangeError, InvalidInputError):
            return self._reply(
                content=self.__i18n_provider.get("extensions.moderation.invalid_time_input_error")
            )

        try:
            await self.__warn_manager.set_warn_decay(context.server_id, decay_threshold)
        except ArgumentOutOfRangeError as error:
            return self._reply(
                content=self.__i18n_provider.get(
                    "extensions.moderation.duration_out_of_range_error",
                    { "min": error.lower_bound, "max": error.upper_bound }
                )
            )

        return WarnDecayToggledResponse(
            author_id=context.author_id,
            is_enabled=True,
            duration=decay_threshold,
            action=ReplyAction(
                content=self.__i18n_provider.get(
                    "extensions.moderation.set_warn_decay_workflow.decay_configured",
                    { "decay_time": textify_timedelta(decay_threshold) }
                )
            )
        )
