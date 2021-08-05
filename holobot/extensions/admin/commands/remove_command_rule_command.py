from .. import CommandRuleManagerInterface
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.utils import has_channel_permission, reply
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class RemoveCommandRuleCommand(CommandBase):
    def __init__(self, rule_manager: CommandRuleManagerInterface) -> None:
        super().__init__("removerule")
        self.__command_rule_manager: CommandRuleManagerInterface = rule_manager
        self.group_name = "admin"
        self.subgroup_name = "commands"
        self.description = "Removes the specified command rule."
        self.options = [
            create_option("identifier", "The identifier of the rule.", SlashCommandOptionType.INTEGER, True)
        ]
        
    async def execute(self, context: SlashContext, identifier: int) -> None:
        if not has_channel_permission(context, context.author, lambda permissions: permissions.administrator):
            await reply(context, "You don't have the required permissions to use this command.")
            return

        await self.__command_rule_manager.remove_rule(identifier)
        await reply(context, "The rule has been removed.")
