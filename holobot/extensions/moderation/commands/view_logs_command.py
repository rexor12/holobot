from .moderation_command_base import ModerationCommandBase
from ..enums import ModeratorPermission
from discord_slash.context import SlashContext
from holobot.discord.sdk.commands import CommandInterface
from holobot.discord.sdk.utils import reply
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class ViewLogsCommand(ModerationCommandBase):
    def __init__(self) -> None:
        super().__init__("view")
        self.group_name = "moderation"
        self.subgroup_name = "logs"
        self.description = "Displays the moderation logs."
        self.required_moderator_permissions = ModeratorPermission.VIEW_LOGS
    
    async def execute(self, context: SlashContext) -> None:
        await reply(context, "logs.")
