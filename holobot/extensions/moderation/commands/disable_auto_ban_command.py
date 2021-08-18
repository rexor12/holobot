from .moderation_command_base import ModerationCommandBase
from .responses import AutoBanToggledResponse
from ..managers import IWarnManager
from discord_slash.context import SlashContext
from holobot.discord.sdk.commands import CommandInterface, CommandResponse
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.utils import reply
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class DisableAutoBanCommand(ModerationCommandBase):
    def __init__(self, warn_manager: IWarnManager) -> None:
        super().__init__("disableban")
        self.group_name = "moderation"
        self.subgroup_name = "auto"
        self.description = "Disables automatic user banishment."
        self.required_permissions = Permission.ADMINISTRATOR
        self.__warn_manager: IWarnManager = warn_manager
    
    async def execute(self, context: SlashContext) -> CommandResponse:
        await self.__warn_manager.disable_auto_ban(str(context.guild_id))
        await reply(context, "Users won't be banned automatically anymore.")
        return AutoBanToggledResponse(
            author_id=str(context.author_id)
        )
