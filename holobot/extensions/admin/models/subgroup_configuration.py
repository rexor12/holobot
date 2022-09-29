from dataclasses import dataclass, field

from .command_configuration import CommandConfiguration

@dataclass
class SubgroupConfiguration:
    Name: str
    CanDisable: bool = True
    Commands: list[CommandConfiguration] = field(default_factory=list)

    @property
    def commands_by_name(self) -> dict[str, CommandConfiguration]:
        return self.__commands_by_name

    def __post_init__(self) -> None:
        self.__commands_by_name = {
            command.Name: command
            for command in self.Commands
        }
