from .moderation_command_base import ModerationCommandBase
from .responses import LogChannelToggledResponse
from ..managers import ILogManager
from discord_slash import SlashCommandOptionType
from discord_slash.context import SlashContext
from discord_slash.utils.manage_commands import create_option
from holobot.discord.sdk.commands import CommandInterface, CommandResponse
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.utils import get_channel_id_from_mention, reply
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class SetLogChannelCommand(ModerationCommandBase):
    def __init__(self, log_manager: ILogManager) -> None:
        super().__init__("setchannel")
        self.group_name = "moderation"
        self.subgroup_name = "logs"
        self.description = "Sets the channel in which moderation actions are logged."
        self.options = [
            create_option("channel", "The mention of the channel to publish moderation logs in.", SlashCommandOptionType.STRING, True)
        ]
        self.required_permissions = Permission.ADMINISTRATOR
        self.__log_manager: ILogManager = log_manager
    
    async def execute(self, context: SlashContext, channel: str) -> CommandResponse:
        channel_id = get_channel_id_from_mention(channel)
        if not channel_id:
            await reply(context, "You must mention a channel correctly.")
            return CommandResponse()

        await self.__log_manager.set_log_channel(str(context.guild_id), channel_id)
        await reply(context, f"Moderation actions will be logged in {channel}. Make sure I have the required permissions to send messages there.")
        return LogChannelToggledResponse(
            author_id=str(context.author_id),
            is_enabled=True,
            channel_id=channel_id
        )
