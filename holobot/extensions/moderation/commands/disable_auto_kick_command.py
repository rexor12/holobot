from .moderation_command_base import ModerationCommandBase
from .responses import AutoKickToggledResponse
from ..managers import IWarnManager
from discord_slash.context import SlashContext
from holobot.discord.sdk.commands import CommandInterface, CommandResponse
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.utils import reply
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
    
    async def execute(self, context: SlashContext) -> CommandResponse:
        await self.__warn_manager.disable_auto_kick(str(context.guild_id))
        await reply(context, "Users won't be kicked automatically anymore.")
        return AutoKickToggledResponse(
            author_id=str(context.author_id)
        )
