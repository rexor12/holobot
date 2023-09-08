from ..enums import Permission

class PermissionError(Exception):
    @property
    def permissions(self) -> Permission | None:
        return self.__permissions

    @permissions.setter
    def permissions(self, value: Permission | None) -> None:
        self.__permissions = value

    def __init__(self, permissions: Permission | None, *args: object) -> None:
        super().__init__(*args)
        self.permissions = permissions

    def __str__(self) -> str:
        return f"{super().__str__()}\nPermissions: {self.permissions}"
