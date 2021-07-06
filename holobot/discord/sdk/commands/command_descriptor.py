from typing import Optional

class CommandDescriptor:
    def __init__(self, name: str, group: Optional[str] = None, sub_group: Optional[str] = None) -> None:
        self.group = group
        self.sub_group = sub_group
        self.name = name
    
    @property
    def group(self) -> Optional[str]:
        return self.__group
    
    @group.setter
    def group(self, value: Optional[str]) -> None:
        self.__group = value
    
    @property
    def sub_group(self) -> Optional[str]:
        return self.__sub_group
    
    @sub_group.setter
    def sub_group(self, value: Optional[str]) -> None:
        self.__sub_group = value
    
    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        self.__name = value
