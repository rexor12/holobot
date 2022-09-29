from dataclasses import dataclass, field

from .command_configuration import CommandConfiguration
from .subgroup_configuration import SubgroupConfiguration

@dataclass
class GroupConfiguration:
    Name: str
    CanDisable: bool = True
    Subgroups: list[SubgroupConfiguration] = field(default_factory=list)
    Commands: list[CommandConfiguration] = field(default_factory=list)

    @property
    def subgroups_by_name(self) -> dict[str, SubgroupConfiguration]:
        return self.__subgroups_by_name

    @property
    def commands_by_name(self) -> dict[str, CommandConfiguration]:
        return self.__commands_by_name

    def __post_init__(self) -> None:
        self.__subgroups_by_name = {
            subgroup.Name: subgroup
            for subgroup in self.Subgroups
        }
        self.__commands_by_name = {
            command.Name: command
            for command in self.Commands
        }
