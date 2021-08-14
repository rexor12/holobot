from .moderation_command_base import ModerationCommandBase
from .responses import WarnDecayToggledResponse
from ..managers import IWarnManager
from discord_slash.context import SlashContext
from holobot.discord.sdk.commands import CommandInterface, CommandResponse
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.utils import reply
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class ClearWarnDecayCommand(ModerationCommandBase):
    def __init__(self, warn_manager: IWarnManager) -> None:
        super().__init__("cleardecay")
        self.group_name = "moderation"
        self.subgroup_name = "warns"
        self.description = "Disables automatic warn strike removal."
        self.required_permissions = Permission.ADMINISTRATOR
        self.__warn_manager: IWarnManager = warn_manager
    
    async def execute(self, context: SlashContext) -> CommandResponse:
        await self.__warn_manager.set_warn_decay(str(context.guild_id), None)
        await reply(context, "Warn strikes won't be removed automatically anymore.")
        return WarnDecayToggledResponse(
            author_id=str(context.author_id)
        )
