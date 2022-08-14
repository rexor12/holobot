from typing import Optional

from .interactables.decorators import moderation_command
from .responses import AutoMuteToggledResponse
from ..managers import IWarnManager
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.chrono import parse_interval
from holobot.sdk.exceptions import ArgumentOutOfRangeError
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class SetAutoMuteWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        warn_manager: IWarnManager
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__warn_manager = warn_manager

    @moderation_command(
        description="Enables automatic muting of people with warn strikes.",
        name="setmute",
        group_name="moderation",
        subgroup_name="auto",
        options=(
            Option("warn_count", "The number of warns after which a user is automatically muted.", OptionType.INTEGER,),
            Option("duration", "The duration after which the user is automatically unmuted. Eg. 1d, 1h or 30m.", is_mandatory=False)
        ),
        required_permissions=Permission.ADMINISTRATOR
    )
    async def set_auto_mute(
        self,
        context: ServerChatInteractionContext,
        warn_count: int,
        duration: Optional[str] = None
    ) -> InteractionResponse:
        mute_duration = parse_interval(duration.strip()) if duration is not None else None
        try:
            await self.__warn_manager.enable_auto_mute(context.server_id, warn_count, mute_duration)
        except ArgumentOutOfRangeError as error:
            if error.argument_name == "duration":
                return InteractionResponse(
                    action=ReplyAction(
                        content=self.__i18n_provider.get(
                            "extensions.moderation.duration_out_of_range_error",
                            { "min": error.lower_bound, "max": error.upper_bound }
                        )
                    )
                )
            return InteractionResponse(
                action=ReplyAction(
                    content=self.__i18n_provider.get(
                        "extensions.moderation.warn_count_out_of_range_error",
                        { "min": error.lower_bound, "max": error.upper_bound }
                    )
                )
            )

        return AutoMuteToggledResponse(
            author_id=context.author_id,
            is_enabled=True,
            warn_count=warn_count,
            duration=mute_duration,
            action=ReplyAction(
                content=self.__i18n_provider.get(
                    "extensions.moderation.set_auto_mute_workflow.automute_configured",
                    { "warns": warn_count }
                )
            )
        )
