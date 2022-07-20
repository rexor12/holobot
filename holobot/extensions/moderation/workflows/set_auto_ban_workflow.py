from .interactables.decorators import moderation_command
from .responses import AutoBanToggledResponse
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
class SetAutoBanWorkflow(WorkflowBase):
    def __init__(self, warn_manager: IWarnManager) -> None:
        super().__init__()
        self.__warn_manager: IWarnManager = warn_manager

    @moderation_command(
        description="Enables automatic banning of people with warn strikes.",
        name="setban",
        group_name="moderation",
        subgroup_name="auto",
        options=(
            Option("warn_count", "The number of warns after which a user is automatically banned.", OptionType.INTEGER),
        ),
        required_permissions=Permission.ADMINISTRATOR
    )
    async def set_auto_ban(
        self,
        context: ServerChatInteractionContext,
        warn_count: int
    ) -> InteractionResponse:
        try:
            await self.__warn_manager.enable_auto_ban(context.server_id, warn_count)
        except ArgumentOutOfRangeError as error:
            return InteractionResponse(
                action=ReplyAction(content=f"The warn count must be between {error.lower_bound} and {error.upper_bound}.")
            )

        return AutoBanToggledResponse(
            author_id=context.author_id,
            is_enabled=True,
            warn_count=warn_count,
            action=ReplyAction(content="Auto ban has been configured.")
        )