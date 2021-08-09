from .moderation_command_base import ModerationCommandBase
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.utils import reply
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class EnableAutoLogCommand(ModerationCommandBase):
    def __init__(self) -> None:
        super().__init__("enable")
        self.group_name = "moderation"
        self.subgroup_name = "autolog"
        self.description = "Enables automatic logging to a channel."
        self.options = [
            create_option("channel", "The mention of the channel to use.", SlashCommandOptionType.STRING, True)
        ]
        self.required_permissions = Permission.ADMINISTRATOR
    
    async def execute(self, context: SlashContext, channel: str) -> None:
        await reply(context, f"channel: {channel}")
