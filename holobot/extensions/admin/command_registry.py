from .command_registry_interface import CommandRegistryInterface
from .models import GroupConfiguration
from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from holobot.sdk.utils import assert_not_none
from typing import Dict, Optional, Tuple

DEFAULT_GROUP_NAME = ""

@injectable(CommandRegistryInterface)
class CommandRegistry(CommandRegistryInterface):
    def __init__(self, configurator: ConfiguratorInterface, log: LogInterface) -> None:
        super().__init__()
        self.__log: LogInterface = log.with_name("Admin", "CommandRegistry")
        # group -> sub-group -> name
        self.__registry: Dict[str, GroupConfiguration] = {}
        self.__register_commands(configurator)
    
    def command_exists(self, command_name: str, group_name: Optional[str] = None, subgroup_name: Optional[str] = None) -> bool:
        assert_not_none(command_name, "command_name")
        group_name = group_name or DEFAULT_GROUP_NAME
        if (group := self.__registry.get(group_name, None)) is None:
            return False

        if not subgroup_name:
            return command_name in group.commands.keys()
        
        if (subgroup := group.subgroups.get(subgroup_name, None)) is None:
            return False
        
        return command_name in subgroup.commands.keys()
    
    def group_exists(self, group_name: str) -> bool:
        assert_not_none(group_name, "group_name")
        return group_name in self.__registry.keys()
    
    def get_commands(self) -> Dict[str, Dict[str, Tuple[str, ...]]]:
        result: Dict[str, Dict[str, Tuple[str, ...]]] = {}
        for group_name, group_config in self.__registry.items():
            result[group_name] = group = {}
            group[DEFAULT_GROUP_NAME] = tuple([command_name for command_name in group_config.commands.keys()])
            for subgroup_name, subgroup_config in group_config.subgroups.items():
                group[subgroup_name] = tuple([command_name for command_name in subgroup_config.commands.keys()])
        return result
    
    def __register_commands(self, configurator: ConfiguratorInterface) -> None:
        for group_json in configurator.get("Admin", "CommandGroups", {}):
            group = GroupConfiguration.from_json(group_json)
            self.__registry[group.name] = group
            self.__log.debug(f"Registered command group configuration. {{ Group = {group.name} }}")
