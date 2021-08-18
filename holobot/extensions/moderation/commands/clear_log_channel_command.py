from .moderation_command_base import ModerationCommandBase
from .responses import LogChannelToggledResponse
from ..managers import ILogManager
from discord_slash.context import SlashContext
from holobot.discord.sdk.commands import CommandInterface, CommandResponse
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.utils import reply
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
    
    async def execute(self, context: SlashContext) -> CommandResponse:
        await self.__log_manager.set_log_channel(str(context.guild_id), None)
        await reply(context, f"Moderation actions won't be logged anymore.")
        return LogChannelToggledResponse(
            author_id=str(context.author_id)
        )
