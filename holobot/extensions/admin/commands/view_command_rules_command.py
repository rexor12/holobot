from .. import CommandRuleManagerInterface
from discord.embeds import Embed
from discord.ext.commands.context import Context
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from holobot.discord.components import DynamicPager
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.utils import reply
from holobot.sdk.integration import MessagingInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from typing import Optional, Union

@injectable(CommandInterface)
class ViewCommandRulesCommand(CommandBase):
    def __init__(self, command_manager: CommandRuleManagerInterface, log: LogInterface, messaging: MessagingInterface) -> None:
        super().__init__("viewrules")
        self.__command_manager: CommandRuleManagerInterface = command_manager
        self.__log: LogInterface = log.with_name("Admin", "ViewCommandRulesCommand")
        self.__messaging: MessagingInterface = messaging
        self.group_name = "admin"
        self.subgroup_name = "commands"
        self.description = "Lists the rules set on this server."
        self.options = [
            create_option("group", "The name of the command group, such as \"admin\".", SlashCommandOptionType.STRING, False),
            create_option("subgroup", "The name of the command sub-group, such as \"commands\" under \"admin\".", SlashCommandOptionType.STRING, False)
        ]
        
    async def execute(self, context: SlashContext, group: Optional[str] = None, subgroup: Optional[str] = None) -> None:
        if not group and subgroup:
            await reply(context, "You can specify a subgroup if and only if you specify a group, too.")
            return
        
        async def create_filtered_embed(context: Union[Context, SlashContext], page: int, page_size: int) -> Optional[Embed]:
            start_offset = page * page_size
            rules = await self.__command_manager.get_rules_by_server(str(context.guild.id), start_offset, page_size)
            if len(rules) == 0:
                return None

            embed = Embed(
                title="Command rules",
                description="The list of command rules set on this server.",
                color=0xeb7d00
            )

            for rule in rules:
                embed.add_field(
                    name=f"Rule #{rule.id}",
                    value=rule.textify(),
                    inline=False
                )
            return embed
        
        await DynamicPager(self.__messaging, self.__log, context, create_filtered_embed)
