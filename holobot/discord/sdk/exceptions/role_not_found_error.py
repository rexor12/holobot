class RoleNotFoundError(Exception):
    def __init__(self, server_id: str, role_id: str, *args: object) -> None:
        super().__init__(*args)
        self.__server_id: str = server_id
        self.__role_id: str = role_id

    @property
    def server_id(self) -> str:
        return self.__server_id

    @property
    def role_id(self) -> str:
        return self.__role_id
