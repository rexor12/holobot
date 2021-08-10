from .moderation_command_base import ModerationCommandBase
from ..enums import ModeratorPermission
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from holobot.discord.sdk.commands import CommandInterface
from holobot.discord.sdk.utils import reply
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class KickUserCommand(ModerationCommandBase):
    def __init__(self) -> None:
        super().__init__("kick")
        self.group_name = "moderation"
        self.description = "Kicks a user from the server. The user can rejoin with an invitation."
        self.options = [
            create_option("user", "The mention of the user to kick.", SlashCommandOptionType.STRING, True)
        ]
        self.required_moderator_permissions = ModeratorPermission.MUTE
    
    async def execute(self, context: SlashContext, user: str) -> None:
        await reply(context, "kick.")
