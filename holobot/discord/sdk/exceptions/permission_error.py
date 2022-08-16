from ..enums import Permission

class PermissionError(Exception):
    def __init__(self, permissions: Permission | None, *args: object) -> None:
        super().__init__(*args)
        self.__permissions: Permission | None = permissions

    @property
    def permissions(self) -> Permission | None:
        return self.__permissions
