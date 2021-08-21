from ..enums import ModeratorPermission
from holobot.discord.sdk.context_menus import UserMenuItemBase

class ModerationMenuItemBase(UserMenuItemBase):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.required_moderator_permissions = ModeratorPermission.NONE
    
    @property
    def required_moderator_permissions(self) -> ModeratorPermission:
        return self.__required_moderator_permissions
    
    @required_moderator_permissions.setter
    def required_moderator_permissions(self, value: ModeratorPermission) -> None:
        self.__required_moderator_permissions = value
