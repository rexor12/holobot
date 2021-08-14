from .. import CommandRuleManagerInterface
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from holobot.discord.sdk.commands import CommandBase, CommandInterface, CommandResponse
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.utils import reply
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class RemoveAllCommandRulesCommand(CommandBase):
    def __init__(self, rule_manager: CommandRuleManagerInterface) -> None:
        super().__init__("removeall")
        self.__command_rule_manager: CommandRuleManagerInterface = rule_manager
        self.group_name = "admin"
        self.subgroup_name = "commands"
        self.description = "Removes ALL command rules specified for this server."
        self.options = [
            create_option("confirmation", "Type \"confirm\" if you are sure about this.", SlashCommandOptionType.STRING, True)
        ]
        self.required_permissions = Permission.ADMINISTRATOR
        
    async def execute(self, context: SlashContext, confirmation: str) -> CommandResponse:
        if confirmation != "confirm":
            await reply(context, "No rules have been removed. You must confirm your intention correctly.")
            return CommandResponse()
        await self.__command_rule_manager.remove_rules_by_server(str(context.guild_id))
        await reply(context, "ALL rules specified for this server have been removed.")
        return CommandResponse()
