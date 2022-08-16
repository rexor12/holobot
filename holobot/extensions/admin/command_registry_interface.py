from abc import ABCMeta, abstractmethod

from .models import CommandConfiguration, GroupConfiguration, SubgroupConfiguration

class CommandRegistryInterface(metaclass=ABCMeta):
    @abstractmethod
    def command_exists(
        self,
        command_name: str,
        group_name: str | None = None,
        subgroup_name: str | None = None
    ) -> bool:
        ...

    @abstractmethod
    def group_exists(self, group_name: str) -> bool:
        ...

    @abstractmethod
    def get_group(self, group_name: str) -> GroupConfiguration | None:
        ...

    @abstractmethod
    def get_subgroup(
        self,
        group_name: str,
        subgroup_name: str
    ) -> SubgroupConfiguration | None:
        ...

    @abstractmethod
    def get_command(
        self,
        command_name: str,
        group_name: str | None = None,
        subgroup_name: str | None = None
    ) -> CommandConfiguration | None:
        ...
