from __future__ import annotations

from typing import Any

from .command_configuration import CommandConfiguration
from .subgroup_configuration import SubgroupConfiguration

class GroupConfiguration:
    def __init__(self, name: str) -> None:
        self.name = name
        self.can_disable = True
        self.subgroups = {}
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
    def subgroups(self) -> dict[str, SubgroupConfiguration]:
        return self.__subgroups

    @subgroups.setter
    def subgroups(self, value: dict[str, SubgroupConfiguration]) -> None:
        self.__subgroups = value

    @property
    def commands(self) -> dict[str, CommandConfiguration]:
        return self.__commands

    @commands.setter
    def commands(self, value: dict[str, CommandConfiguration]) -> None:
        self.__commands = value

    @staticmethod
    def from_json(name: str, json: dict[str, Any]) -> GroupConfiguration:
        config = GroupConfiguration(name)
        config.can_disable = json.get("CanDisable", True)
        for key, value in json.get("Subgroups", {}).items():
            config.subgroups[key] = SubgroupConfiguration.from_json(key, config.can_disable, value)
        for key, value in json.get("Commands", {}).items():
            config.commands[key] = CommandConfiguration.from_json(key, config.can_disable, value)
        return config
