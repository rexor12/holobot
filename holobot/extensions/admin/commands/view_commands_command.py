from .. import CommandRegistryInterface
from discord.embeds import Embed
from discord.ext.commands.context import Context
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from holobot.discord.components import DynamicPager
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.utils import get_author_id, reply
from holobot.sdk.integration import MessagingInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from typing import Dict, Generator, List, Optional, Tuple, Union

import re

channel_regex = re.compile(r"^<#(?P<id>\d+)>$")

@injectable(CommandInterface)
class ViewCommandsCommand(CommandBase):
    def __init__(self, command_registry: CommandRegistryInterface, log: LogInterface, messaging: MessagingInterface) -> None:
        super().__init__("view")
        self.__command_registry: CommandRegistryInterface = command_registry
        self.__log: LogInterface = log.with_name("Admin", "ViewCommandsCommand")
        self.__messaging: MessagingInterface = messaging
        self.group_name = "admin"
        self.subgroup_name = "commands"
        self.description = "Lists the commands with settings capabilities."
        self.options = [
            create_option("group", "The name of the command group, such as \"admin\".", SlashCommandOptionType.STRING, False),
            create_option("subgroup", "The name of the command sub-group, such as \"commands\" under \"admin\".", SlashCommandOptionType.STRING, False)
        ]
        self.__commands: Dict[str, Dict[str, Tuple[str, ...]]] = self.__command_registry.get_commands()
        
    async def execute(self, context: SlashContext, group: Optional[str] = None, subgroup: Optional[str] = None) -> None:
        if not group and subgroup:
            await reply(context, "You can specify a subgroup if and only if you specify a group, too.")
            return
        
        filtered_commands = self.__commands
        has_commands = len(filtered_commands) > 0
        if group:
            filtered_commands = { group: self.__commands.get(group, {}) }
            has_commands = len(filtered_commands[group]) > 0
            if subgroup:
                filtered_commands = { subgroup: filtered_commands.get(subgroup, {}) }
                has_commands = len(filtered_commands[group][subgroup]) > 0
        if not has_commands:
            await reply(context, "There are no commands matching your query.")
            return
        
        flattened_commands = tuple(ViewCommandsCommand.__flatten_commands(filtered_commands))
        async def create_filtered_embed(context: Union[Context, SlashContext], page: int, page_size: int) -> Optional[Embed]:
            start_offset = page * page_size
            if start_offset >= len(flattened_commands):
                return None
            
            if start_offset + page_size > len(flattened_commands):
                page_size = len(flattened_commands) - start_offset
            
            embed = Embed(
                title="Commands",
                description="The list of all available commands.",
                color=0xeb7d00
            )

            for index in range(start_offset, start_offset + page_size):
                command = flattened_commands[index]
                embed.add_field(
                    name="",
                    value=f"/{command[0]} {command[1]} {command[2]}"
                )
        
        await DynamicPager(self.__messaging, self.__log, context, create_filtered_embed)
    
    @staticmethod
    def __flatten_commands(descriptors: Dict[str, Dict[str, Tuple[str, ...]]]):
        for group_name, subgroups in descriptors:
            for subgroup_name, commands in subgroups:
                for command_name in commands:
                    yield (group_name, subgroup_name, command_name)

    async def __create_page_embed(self, context: Union[Context, SlashContext], page: int, page_size: int) -> Optional[Embed]:
        if len(self.__commands) == 0:
            return None
        
        embed = Embed(
            title="Commands",
            description="The list of all available commands.",
            color=0xeb7d00
        )
        
        # for item in items:
        #     embed.add_field(
        #         name=f"#{item.id}",
        #         value=item.message,
        #         inline=False
        #     )
        return embed
