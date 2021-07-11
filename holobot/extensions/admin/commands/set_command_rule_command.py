from .. import CommandRuleManagerInterface
from ..enums import RuleState
from ..exceptions import InvalidCommandError
from ..models import CommandRule
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_choice, create_option
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.utils import reply
from holobot.sdk.ioc import ServiceCollectionInterface
from holobot.sdk.ioc.decorators import injectable
from typing import Optional

import re

channel_regex = re.compile(r"^<#(?P<id>\d+)>$")

@injectable(CommandInterface)
class SetCommandRuleCommand(CommandBase):
    def __init__(self, services: ServiceCollectionInterface) -> None:
        super().__init__(services, "setrule")
        self.__command_rule_manager: CommandRuleManagerInterface = services.get(CommandRuleManagerInterface)
        self.group_name = "admin"
        self.subgroup_name = "commands"
        self.description = "Adds a new or modifies an existing rule for one or more commands."
        self.options = [
            create_option("state", "Whether to allow or forbid commands.", SlashCommandOptionType.STRING, True, [
                create_choice("Allow", "Allow"),
                create_choice("Forbid", "Forbid")
            ]),
            create_option("group", "An entire command group, such as \"admin\".", SlashCommandOptionType.STRING, False),
            create_option("command", "A command inside a command group, such as \"roll\".", SlashCommandOptionType.STRING, False),
            create_option("channel", "The link of the applicable channel.", SlashCommandOptionType.STRING, False)
        ]
        
    async def execute(self, context: SlashContext, state: str, group: Optional[str] = None, command: Optional[str] = None, channel: Optional[str] = None) -> None:
        if context.guild is None:
            await reply(context, "Command rules can be defined in servers only.")
            return
        channel_id: Optional[str] = None
        if channel is not None:
            if (channel_match := channel_regex.match(channel)) is None:
                await reply(context, "Invalid channel. Did you link it properly?")
                return
            channel_id = channel_match.group("id")
        rule = CommandRule()
        rule.created_by = str(context.author_id)
        rule.server_id = str(context.guild.id)
        rule.state = RuleState.parse(state)
        rule.group = group
        rule.command = command
        rule.channel_id = channel_id
        try:
            await self.__command_rule_manager.set_rule(rule)
            await reply(context, f"Your rule has been set: {rule.textify()}")
        except InvalidCommandError:
            await reply(context, "This command doesn't exist or rules cannot be set for it.")
