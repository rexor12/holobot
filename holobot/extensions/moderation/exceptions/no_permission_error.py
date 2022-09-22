from ..enums import ModeratorPermission

class NoPermissionError(Exception):
    def __init__(
        self,
        required_permissions: ModeratorPermission,
        actual_permissions: ModeratorPermission,
        *args: object
    ) -> None:
        super().__init__(*args)
        self.__required_permissions: ModeratorPermission = required_permissions
        self.__actual_permissions: ModeratorPermission = actual_permissions

    @property
    def required_permissions(self) -> ModeratorPermission:
        return self.__required_permissions

    @property
    def actual_permissions(self) -> ModeratorPermission:
        return self.__actual_permissions
