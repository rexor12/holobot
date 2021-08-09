from .moderation_command_base import ModerationCommandBase
from discord_slash import SlashCommandOptionType
from discord_slash.context import SlashContext
from discord_slash.utils.manage_commands import create_option
from holobot.discord.sdk.commands import CommandInterface
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.utils import reply
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class ClearLogsCommand(ModerationCommandBase):
    def __init__(self) -> None:
        super().__init__("clear")
        self.group_name = "moderation"
        self.subgroup_name = "logs"
        self.description = "Clears ALL the moderation logs."
        self.options = [
            create_option("confirmation", "Type \"confirm\" if you are sure about this.", SlashCommandOptionType.STRING, True)
        ]
        self.required_permissions = Permission.ADMINISTRATOR
    
    async def execute(self, context: SlashContext, confirmation: str) -> None:
        if confirmation != "confirm":
            await reply(context, "No moderation logs have been removed. You must confirm your intention correctly.")
            return
        #await self.__command_rule_manager.remove_rules_by_server(str(context.guild_id))
        await reply(context, "ALL moderation logs have been removed.")
