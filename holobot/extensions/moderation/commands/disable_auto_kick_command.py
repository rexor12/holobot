from .moderation_command_base import ModerationCommandBase
from .responses import AutoKickToggledResponse
from ..managers import IWarnManager
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, ServerChatInteractionContext
from holobot.discord.sdk.enums import Permission
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class DisableAutoKickCommand(ModerationCommandBase):
    def __init__(self, warn_manager: IWarnManager) -> None:
        super().__init__("disablekick")
        self.group_name = "moderation"
        self.subgroup_name = "auto"
        self.description = "Disables automatic user kicking."
        self.required_permissions = Permission.ADMINISTRATOR
        self.__warn_manager: IWarnManager = warn_manager
    
    async def execute(self, context: ServerChatInteractionContext) -> CommandResponse:
        await self.__warn_manager.disable_auto_kick(context.server_id)
        return AutoKickToggledResponse(
            author_id=context.author_id,
            action=ReplyAction(content="Users won't be kicked automatically anymore.")
        )
