from .models import CommandConfiguration, GroupConfiguration, SubgroupConfiguration
from abc import ABCMeta, abstractmethod
from typing import Optional

class CommandRegistryInterface(metaclass=ABCMeta):
    @abstractmethod
    def command_exists(
        self,
        command_name: str,
        group_name: Optional[str] = None,
        subgroup_name: Optional[str] = None
    ) -> bool:
        ...

    @abstractmethod
    def group_exists(self, group_name: str) -> bool:
        ...

    @abstractmethod
    def get_group(self, group_name: str) -> Optional[GroupConfiguration]:
        ...

    @abstractmethod
    def get_subgroup(
        self,
        group_name: str,
        subgroup_name: str
    ) -> Optional[SubgroupConfiguration]:
        ...

    @abstractmethod
    def get_command(
        self,
        command_name: str,
        group_name: Optional[str] = None,
        subgroup_name: Optional[str] = None
    ) -> Optional[CommandConfiguration]:
        ...
