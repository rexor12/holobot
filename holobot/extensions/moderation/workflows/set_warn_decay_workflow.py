from .interactables.decorators import moderation_command
from .responses import WarnDecayToggledResponse
from ..managers import IWarnManager
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.chrono import parse_interval
from holobot.sdk.exceptions import ArgumentOutOfRangeError
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class SetWarnDecayWorkflow(WorkflowBase):
    def __init__(self, warn_manager: IWarnManager) -> None:
        super().__init__()
        self.__warn_manager: IWarnManager = warn_manager

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
        decay_threshold = parse_interval(duration.strip())
        try:
            await self.__warn_manager.set_warn_decay(context.server_id, decay_threshold)
        except ArgumentOutOfRangeError as error:
            return InteractionResponse(
                action=ReplyAction(content=f"The duration must be between {error.lower_bound} and {error.upper_bound}.")
            )

        return WarnDecayToggledResponse(
            author_id=context.author_id,
            is_enabled=True,
            duration=decay_threshold,
            action=ReplyAction(content="The warn decay time has been set.")
        )
