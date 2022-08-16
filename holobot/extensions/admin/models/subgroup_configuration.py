from .command_configuration import CommandConfiguration
from typing import Any

class SubgroupConfiguration:
    def __init__(self, name: str) -> None:
        self.name = name
        self.can_disable = True
        self.commands = {}

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        self.__name = value

    @property
    def can_disable(self) -> bool:
        return self.__can_disable

    @can_disable.setter
    def can_disable(self, value: bool) -> None:
        self.__can_disable = value

    @property
    def commands(self) -> dict[str, CommandConfiguration]:
        return self.__commands

    @commands.setter
    def commands(self, value: dict[str, CommandConfiguration]) -> None:
        self.__commands = value

    @staticmethod
    def from_json(name: str, can_disable_parent: bool, json: dict[str, Any]) -> 'SubgroupConfiguration':
        config = SubgroupConfiguration(name)
        config.can_disable = json.get("CanDisable", can_disable_parent)
        for key, value in json.get("Commands", {}).items():
            config.commands[key] = CommandConfiguration.from_json(key, config.can_disable, value)
        return config
