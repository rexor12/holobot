from .moderation_command_base import ModerationCommandBase
from .responses import AutoBanToggledResponse
from ..managers import IWarnManager
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from holobot.discord.sdk.commands import CommandInterface, CommandResponse
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.utils import reply
from holobot.sdk.exceptions import ArgumentOutOfRangeError
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class SetAutoBanCommand(ModerationCommandBase):
    def __init__(self, warn_manager: IWarnManager) -> None:
        super().__init__("setban")
        self.group_name = "moderation"
        self.subgroup_name = "auto"
        self.description = "Enables automatic banning of people with warn strikes."
        self.options = [
            create_option("warn_count", "The number of warns after which a user is automatically banned.", SlashCommandOptionType.INTEGER, True)
        ]
        self.required_permissions = Permission.ADMINISTRATOR
        self.__warn_manager: IWarnManager = warn_manager
    
    async def execute(self, context: SlashContext, warn_count: int) -> CommandResponse:
        try:
            await self.__warn_manager.enable_auto_ban(str(context.guild_id), warn_count)
            await reply(context, "Auto ban has been configured.")
        except ArgumentOutOfRangeError as error:
            await reply(context, f"The warn count must be between {error.lower_bound} and {error.upper_bound}.")
            return CommandResponse()
        return AutoBanToggledResponse(
            author_id=str(context.author_id),
            is_enabled=True,
            warn_count=warn_count
        )
