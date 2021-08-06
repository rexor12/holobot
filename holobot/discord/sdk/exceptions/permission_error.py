from ..enums import Permission
from typing import Optional

class PermissionError(Exception):
    def __init__(self, permissions: Optional[Permission], *args: object) -> None:
        super().__init__(*args)
        self.__permissions: Optional[Permission] = permissions
    
    @property
    def permissions(self) -> Optional[Permission]:
        return self.__permissions
