from .command_registry_interface import CommandRegistryInterface
from .models import CommandConfiguration, GroupConfiguration, SubgroupConfiguration
from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from holobot.sdk.utils import assert_not_none
from typing import Dict, Optional

DEFAULT_GROUP_NAME = ""

@injectable(CommandRegistryInterface)
class CommandRegistry(CommandRegistryInterface):
    def __init__(self, configurator: ConfiguratorInterface, log: LogInterface) -> None:
        super().__init__()
        self.__log: LogInterface = log.with_name("Admin", "CommandRegistry")
        self.__registry: Dict[str, GroupConfiguration] = self.__parse_command_configs(configurator)

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
        return group_name in self.__registry

    def get_group(self, group_name: str) -> Optional[GroupConfiguration]:
        return self.__registry.get(group_name, None)

    def get_subgroup(
        self,
        group_name: str,
        subgroup_name: str
    ) -> Optional[SubgroupConfiguration]:
        if not (group := self.__registry.get(group_name, None)):
            return None
        return group.subgroups.get(subgroup_name, None)

    def get_command(
        self,
        command_name: str,
        group_name: Optional[str] = None,
        subgroup_name: Optional[str] = None
    ) -> Optional[CommandConfiguration]:
        group_name = group_name or DEFAULT_GROUP_NAME
        if not (group := self.__registry.get(group_name, None)):
            return None
        if not subgroup_name:
            return group.commands.get(command_name, None)
        if not (subgroup := group.subgroups.get(subgroup_name, None)):
            return None
        return subgroup.commands.get(command_name, None)

    def __parse_command_configs(
        self,
        configurator: ConfiguratorInterface
    ) -> Dict[str, GroupConfiguration]:
        configs: Dict[str, GroupConfiguration] = {}
        self.__log.debug("Parsing command group configurations...")
        for name, group_json in configurator.get("Admin", "CommandGroups", {}).items():
            group = GroupConfiguration.from_json(name, group_json)
            configs[group.name] = group
            self.__log.debug(f"Registered command group configuration. {{ Group = {group.name} }}")
        self.__log.debug("Command group parsed.")
        return configs
