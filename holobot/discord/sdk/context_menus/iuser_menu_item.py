from .imenu_item import IMenuItem
from typing import Any

class IUserMenuItem(IMenuItem):
    @property
    def name(self) -> str:
        return self.__name
    
    @name.setter
    def name(self, value: str) -> None:
        self.__name = value

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, IUserMenuItem):
            return False
        return self.name < other.name
