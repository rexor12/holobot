from .. import CommandRuleManagerInterface
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.utils import reply
from holobot.sdk.ioc.decorators import injectable
from typing import Optional

@injectable(CommandInterface)
class TestCommandCommand(CommandBase):
    def __init__(self, rule_manager: CommandRuleManagerInterface) -> None:
        super().__init__("test")
        self.__command_rule_manager: CommandRuleManagerInterface = rule_manager
        self.group_name = "admin"
        self.subgroup_name = "commands"
        self.description = "Tests a command to determine if it can be used in the current channel."
        self.options = [
            create_option("command", "A command inside the command group, such as \"roll\".", SlashCommandOptionType.STRING, True),
            create_option("group", "The command group, such as \"admin\".", SlashCommandOptionType.STRING, False)
        ]
        
    async def execute(self, context: SlashContext, command: str, group: Optional[str] = None) -> None:
        if context.guild is None:
            await reply(context, "Command rules can be defined in servers only.")
            return

        can_execute = await self.__command_rule_manager.can_execute(str(context.guild.id), str(context.channel_id), group, None, command)
        disabled_text = " NOT" if not can_execute else ""
        await reply(context, f"The command CAN{disabled_text} be executed in this channel.")
