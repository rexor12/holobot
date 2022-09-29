from holobot.sdk.configs import IOptions
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.utils import assert_not_none
from .command_registry_interface import CommandRegistryInterface
from .models import CommandConfiguration, CommandOptions, GroupConfiguration, SubgroupConfiguration

DEFAULT_GROUP_NAME = ""

@injectable(CommandRegistryInterface)
class CommandRegistry(CommandRegistryInterface):
    def __init__(
        self,
        logger_factory: ILoggerFactory,
        options: IOptions[CommandOptions]
    ) -> None:
        super().__init__()
        self.__log = logger_factory.create(CommandRegistry)
        self.__registry: dict[str, GroupConfiguration] = {
            command_group.Name: command_group
            for command_group in options.value.CommandGroups
        }

    def command_exists(self, command_name: str, group_name: str | None = None, subgroup_name: str | None = None) -> bool:
        assert_not_none(command_name, "command_name")
        group_name = group_name or DEFAULT_GROUP_NAME
        if not (group := self.__registry.get(group_name)):
            return False

        if not subgroup_name:
            return command_name in group.commands_by_name

        if subgroup := group.subgroups_by_name.get(subgroup_name):
            return command_name in subgroup.commands_by_name

        return False

    def group_exists(self, group_name: str) -> bool:
        assert_not_none(group_name, "group_name")
        return group_name in self.__registry

    def get_group(self, group_name: str) -> GroupConfiguration | None:
        return self.__registry.get(group_name)

    def get_subgroup(self, group_name: str, subgroup_name: str) -> SubgroupConfiguration | None:
        if group := self.__registry.get(group_name):
            return group.subgroups_by_name.get(subgroup_name)
        return None

    def get_command(
        self,
        command_name: str,
        group_name: str | None = None,
        subgroup_name: str | None = None
    ) -> CommandConfiguration | None:
        group_name = group_name or DEFAULT_GROUP_NAME
        if not (group := self.__registry.get(group_name)):
            return None
        if not subgroup_name:
            return group.commands_by_name.get(command_name)
        if subgroup := group.subgroups_by_name.get(subgroup_name):
            return subgroup.commands_by_name.get(command_name)
        return None
