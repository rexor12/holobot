from .. import CommandRegistryInterface, CommandRuleManagerInterface
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.utils import get_channel_id, reply
from holobot.sdk.ioc.decorators import injectable
from typing import Optional

@injectable(CommandInterface)
class TestCommandCommand(CommandBase):
    def __init__(self, command_registry: CommandRegistryInterface, rule_manager: CommandRuleManagerInterface) -> None:
        super().__init__("test")
        self.__command_registry: CommandRegistryInterface = command_registry
        self.__command_rule_manager: CommandRuleManagerInterface = rule_manager
        self.group_name = "admin"
        self.subgroup_name = "commands"
        self.description = "Checks if a command can be used in the current or the specified channel."
        self.options = [
            create_option("command", "The specific command, such as \"roll\".", SlashCommandOptionType.STRING, True),
            create_option("group", "The command group, such as \"admin\".", SlashCommandOptionType.STRING, False),
            create_option("subgroup", "The command subgroup, such as \"commands\".", SlashCommandOptionType.STRING, False),
            create_option("channel", "The channel to test.", SlashCommandOptionType.STRING, False)
        ]
        
    async def execute(self, context: SlashContext, command: str, group: Optional[str] = None, subgroup: Optional[str] = None, channel: Optional[str] = None) -> None:
        if context.guild is None:
            await reply(context, "Command rules can be defined in servers only.")
            return
        
        if not self.__command_registry.command_exists(command, group, subgroup):
            await reply(context, "The command you specified doesn't exist. Did you make a typo?")
            return

        channel_id = get_channel_id(context, channel)
        can_execute = await self.__command_rule_manager.can_execute(str(context.guild.id), channel_id, group, subgroup, command)
        disabled_text = " NOT" if not can_execute else ""
        await reply(context, f"The command CAN{disabled_text} be executed in <#{channel_id}>.")
