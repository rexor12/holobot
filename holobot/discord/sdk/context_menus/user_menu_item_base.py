from .iuser_menu_item import IUserMenuItem
from ..enums import Permission

class UserMenuItemBase(IUserMenuItem):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name
        self.required_permissions = Permission.NONE
