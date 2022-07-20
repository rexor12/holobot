from .interactables.decorators import moderation_command
from .responses import AutoKickToggledResponse
from ..managers import IWarnManager
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.exceptions import ArgumentOutOfRangeError
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class SetAutoKickWorkflow(WorkflowBase):
    def __init__(self, warn_manager: IWarnManager) -> None:
        super().__init__()
        self.__warn_manager: IWarnManager = warn_manager

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
        context: ServerChatInteractionContext,
        warn_count: int
    ) -> InteractionResponse:
        try:
            await self.__warn_manager.enable_auto_kick(context.server_id, warn_count)
        except ArgumentOutOfRangeError as error:
            return InteractionResponse(
                action=ReplyAction(content=f"The warn count must be between {error.lower_bound} and {error.upper_bound}.")
            )

        return AutoKickToggledResponse(
            author_id=context.author_id,
            is_enabled=True,
            warn_count=warn_count,
            action=ReplyAction(content="Auto kick has been configured.")
        )
