from .moderation_command_base import ModerationCommandBase
from .responses import LogChannelToggledResponse
from ..managers import ILogManager
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, ServerChatInteractionContext
from holobot.discord.sdk.enums import Permission
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class ClearLogChannelCommand(ModerationCommandBase):
    def __init__(self, log_manager: ILogManager) -> None:
        super().__init__("clearchannel")
        self.group_name = "moderation"
        self.subgroup_name = "logs"
        self.description = "Disables the logging of moderation actions."
        self.required_permissions = Permission.ADMINISTRATOR
        self.__log_manager: ILogManager = log_manager
    
    async def execute(self, context: ServerChatInteractionContext) -> CommandResponse:
        await self.__log_manager.set_log_channel(context.server_id, None)
        return LogChannelToggledResponse(
            author_id=context.author_id,
            action=ReplyAction(content=f"Moderation actions won't be logged anymore.")
        )
