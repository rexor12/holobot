class RoleNotFoundError(Exception):
    @property
    def server_id(self) -> int:
        return self.__server_id

    @server_id.setter
    def server_id(self, value: int) -> None:
        self.__server_id = value

    @property
    def role_id(self) -> int:
        return self.__role_id

    @role_id.setter
    def role_id(self, value: int) -> None:
        self.__role_id = value

    def __init__(self, server_id: int, role_id: int, *args: object) -> None:
        super().__init__(*args)
        self.server_id = server_id
        self.role_id = role_id

    def __str__(self) -> str:
        return f"{super().__str__()}\nServer ID: {self.server_id}, role ID: {self.role_id}"
