from .. import CommandRegistryInterface
from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, Option, ServerChatInteractionContext
from holobot.discord.sdk.components import Pager
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.models import Embed, EmbedField
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from typing import Dict, Generator, Optional, Tuple

@injectable(CommandInterface)
class ViewCommandsCommand(CommandBase):
    def __init__(self, command_registry: CommandRegistryInterface, log: LogInterface, messaging: IMessaging) -> None:
        super().__init__("view")
        self.__command_registry: CommandRegistryInterface = command_registry
        self.__log: LogInterface = log.with_name("Admin", "ViewCommandsCommand")
        self.__messaging: IMessaging = messaging
        self.group_name = "admin"
        self.subgroup_name = "commands"
        self.description = "Lists the commands with settings capabilities."
        self.options = [
            Option("group", "The name of the command group, such as \"admin\".", is_mandatory=False),
            Option("subgroup", "The name of the command sub-group, such as \"commands\" under \"admin\".", is_mandatory=False)
        ]
        self.required_permissions = Permission.ADMINISTRATOR
        self.__commands: Dict[str, Dict[str, Tuple[str, ...]]] = self.__command_registry.get_commands()
        
    async def execute(self, context: ServerChatInteractionContext, group: Optional[str] = None, subgroup: Optional[str] = None) -> CommandResponse:
        if not group and subgroup:
            return CommandResponse(
                action=ReplyAction(content="You can specify a subgroup if and only if you specify a group, too.")
            )

        filtered_commands = self.__commands
        has_commands = len(filtered_commands) > 0
        if group:
            filtered_commands = { group: self.__commands.get(group, {}) }
            has_commands = len(filtered_commands[group]) > 0
            if subgroup:
                filtered_commands = { subgroup: filtered_commands.get(subgroup, {}) }
                has_commands = len(filtered_commands[group][subgroup]) > 0
        if not has_commands:
            return CommandResponse(
                action=ReplyAction(content="There are no commands matching your query.")
            )
        
        flattened_commands = tuple(ViewCommandsCommand.__flatten_commands(filtered_commands))
        async def create_filtered_embed(context: ServerChatInteractionContext, page: int, page_size: int) -> Optional[Embed]:
            start_offset = page * page_size
            if start_offset >= len(flattened_commands):
                return None
            
            if start_offset + page_size > len(flattened_commands):
                page_size = len(flattened_commands) - start_offset
            
            embed = Embed(
                title="Commands",
                description="The list of commands with settings capabilities.",
                color=0xeb7d00
            )

            for index in range(start_offset, start_offset + page_size):
                command = flattened_commands[index]
                embed.fields.append(EmbedField(
                    name=f"Command #{(index + 1)}",
                    value=(
                        f"> Group: {command[0]}\n"
                        f"> Subgroup: {command[1]}\n"
                        f"> Name: {command[2]}"
                    ),
                    is_inline=False
                ))
            return embed
        
        await Pager(self.__messaging, self.__log, context, create_filtered_embed)
        return CommandResponse()
    
    @staticmethod
    def __flatten_commands(descriptors: Dict[str, Dict[str, Tuple[str, ...]]]) -> Generator[Tuple[str, str, str], None, None]:
        for group_name, subgroups in descriptors.items():
            for subgroup_name, commands in subgroups.items():
                for command_name in commands:
                    yield (group_name, subgroup_name, command_name)
