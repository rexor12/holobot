from .command_configuration import CommandConfiguration
from .subgroup_configuration import SubgroupConfiguration
from typing import Any, Dict

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
    def subgroups(self) -> Dict[str, SubgroupConfiguration]:
        return self.__subgroups
    
    @subgroups.setter
    def subgroups(self, value: Dict[str, SubgroupConfiguration]) -> None:
        self.__subgroups = value
    
    @property
    def commands(self) -> Dict[str, CommandConfiguration]:
        return self.__commands
    
    @commands.setter
    def commands(self, value: Dict[str, CommandConfiguration]) -> None:
        self.__commands = value

    @staticmethod
    def from_json(json: Dict[str, Any]) -> 'GroupConfiguration':
        if (name := json.get("Name", None)) is None:
            raise ValueError("The group must have a name.")
        config = GroupConfiguration(name)
        config.can_disable = json.get("CanDisable", True)
        for key, value in json.get("Subgroups", {}).items():
            config.subgroups[key] = SubgroupConfiguration.from_json(key, config.can_disable, value)
        for key, value in json.get("Commands", {}).items():
            config.commands[key] = CommandConfiguration.from_json(key, config.can_disable, value)
        return config
