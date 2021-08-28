from .moderation_command_base import ModerationCommandBase
from .responses import AutoBanToggledResponse
from ..managers import IWarnManager
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandInterface
from holobot.discord.sdk.commands.enums import OptionType
from holobot.discord.sdk.commands.models import CommandResponse, Option, ServerChatInteractionContext
from holobot.discord.sdk.enums import Permission
from holobot.sdk.exceptions import ArgumentOutOfRangeError
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class SetAutoBanCommand(ModerationCommandBase):
    def __init__(self, warn_manager: IWarnManager) -> None:
        super().__init__("setban")
        self.group_name = "moderation"
        self.subgroup_name = "auto"
        self.description = "Enables automatic banning of people with warn strikes."
        self.options = [
            Option("warn_count", "The number of warns after which a user is automatically banned.", OptionType.INTEGER)
        ]
        self.required_permissions = Permission.ADMINISTRATOR
        self.__warn_manager: IWarnManager = warn_manager
    
    async def execute(self, context: ServerChatInteractionContext, warn_count: int) -> CommandResponse:
        try:
            await self.__warn_manager.enable_auto_ban(context.server_id, warn_count)
        except ArgumentOutOfRangeError as error:
            return CommandResponse(
                action=ReplyAction(content=f"The warn count must be between {error.lower_bound} and {error.upper_bound}.")
            )

        return AutoBanToggledResponse(
            author_id=context.author_id,
            is_enabled=True,
            warn_count=warn_count,
            action=ReplyAction(content="Auto ban has been configured.")
        )
