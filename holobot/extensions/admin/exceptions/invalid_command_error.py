from typing import Optional

class InvalidCommandError(Exception):
    def __init__(self, command_name: Optional[str], group_name: Optional[str], subgroup_name: Optional[str], *args) -> None:
        super().__init__(*args)
        self.command_name = command_name
        self.group_name = group_name
        self.subgroup_name = subgroup_name
    
    @property
    def command_name(self) -> Optional[str]:
        return self.__command_name

    @command_name.setter
    def command_name(self, value: Optional[str]) -> None:
        self.__command_name = value
    
    @property
    def group_name(self) -> Optional[str]:
        return self.__group_name

    @group_name.setter
    def group_name(self, value: Optional[str]) -> None:
        self.__group_name = value
    
    @property
    def subgroup_name(self) -> Optional[str]:
        return self.__subgroup_name

    @subgroup_name.setter
    def subgroup_name(self, value: Optional[str]) -> None:
        self.__subgroup_name = value
