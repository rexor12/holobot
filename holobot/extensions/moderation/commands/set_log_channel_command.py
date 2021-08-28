from .moderation_command_base import ModerationCommandBase
from .responses import LogChannelToggledResponse
from ..managers import ILogManager
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, Option, ServerChatInteractionContext
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.utils import get_channel_id
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class SetLogChannelCommand(ModerationCommandBase):
    def __init__(self, log_manager: ILogManager) -> None:
        super().__init__("setchannel")
        self.group_name = "moderation"
        self.subgroup_name = "logs"
        self.description = "Sets the channel in which moderation actions are logged."
        self.options = [
            Option("channel", "The mention of the channel to publish moderation logs in.")
        ]
        self.required_permissions = Permission.ADMINISTRATOR
        self.__log_manager: ILogManager = log_manager
    
    async def execute(self, context: ServerChatInteractionContext, channel: str) -> CommandResponse:
        channel_id = get_channel_id(channel.strip())
        if not channel_id:
            return CommandResponse(
                action=ReplyAction(content="You must mention a channel correctly.")
            )

        await self.__log_manager.set_log_channel(context.server_id, channel_id)
        return LogChannelToggledResponse(
            author_id=context.author_id,
            is_enabled=True,
            channel_id=channel_id,
            action=ReplyAction(content=f"Moderation actions will be logged in {channel}. Make sure I have the required permissions to send messages there.")
        )
