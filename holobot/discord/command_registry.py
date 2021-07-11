from holobot.discord.sdk.commands import CommandInterface, CommandRegistryInterface
from holobot.sdk.ioc import ServiceCollectionInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from holobot.sdk.utils import assert_not_none
from typing import Any, Dict, Optional, Tuple

DEFAULT_GROUP_NAME = "__DEFAULT_GROUP__"
DEFAULT_SUBGROUP_NAME = "__DEFAULT_SUBGROUP__"

@injectable(CommandRegistryInterface)
class CommandRegistry(CommandRegistryInterface):
    def __init__(self, services: ServiceCollectionInterface) -> None:
        super().__init__()
        self.__log: LogInterface = services.get(LogInterface).with_name("Discord", "CommandRegistry")
        # group -> sub-group -> command
        self.__registry: Dict[str, Dict[str, Dict[str, CommandInterface]]] = {}
        self.__commands: Tuple[CommandInterface, ...] = services.get_all(CommandInterface)
        self.__register_commands(self.__commands)
    
    def command_exists(self, command_name: str, group_name: Optional[str] = None, subgroup_name: Optional[str] = None) -> bool:
        assert_not_none(command_name, "command_name")
        group_name = group_name or DEFAULT_GROUP_NAME
        if (group := self.__registry.get(group_name, None)) is None:
            return False

        subgroup_name = subgroup_name or DEFAULT_SUBGROUP_NAME
        if (subgroup := group.get(subgroup_name, None)) is None:
            return False
        
        return command_name in subgroup.keys()
    
    def group_exists(self, group_name: str) -> bool:
        assert_not_none(group_name, "group_name")
        return group_name in self.__registry.keys()
    
    def get_commands(self) -> Dict[str, Dict[str, Tuple[str, ...]]]:
        result: Dict[str, Dict[str, Tuple[str, ...]]] = {}
        for group_name, subgroups in self.__registry.items():
            result[group_name] = group = {}
            for subgroup_name, commands in subgroups.items():
                print(f"[CommandRegistry] {group_name}, {subgroup_name}, {len(commands.keys())}")
                group[subgroup_name] = tuple([command_name for command_name in commands.keys()])
        return result
    
    def __register_commands(self, commands: Tuple[CommandInterface, ...]) -> None:
        for command in commands:
            self.__log.debug(f"Registering command... {{ Group = {command.group_name}, SubGroup = {command.subgroup_name}, Name = {command.name} }}")
            group_name = command.group_name or DEFAULT_GROUP_NAME
            if (group := self.__registry.get(group_name, None)) is None:
                self.__registry[group_name] = group = {}
            subgroup_name = command.subgroup_name or DEFAULT_SUBGROUP_NAME
            if (subgroup := group.get(subgroup_name, None)) is None:
                group[subgroup_name] = subgroup = {}
            subgroup[command.name] = command
            self.__log.debug(f"Registered command. {{ Group = {command.group_name}, SubGroup = {command.subgroup_name}, Name = {command.name} }}")
