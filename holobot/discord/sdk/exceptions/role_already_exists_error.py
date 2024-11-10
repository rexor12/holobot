class RoleAlreadyExistsError(Exception):
    @property
    def server_id(self) -> int:
        return self.__server_id

    @server_id.setter
    def server_id(self, value: int) -> None:
        self.__server_id = value

    @property
    def role_name(self) -> str:
        return self.__role_name

    @role_name.setter
    def role_name(self, value: str) -> None:
        self.__role_name = value

    def __init__(self, server_id: int, role_name: str, *args: object) -> None:
        super().__init__(*args)
        self.server_id = server_id
        self.role_name = role_name

    def __str__(self) -> str:
        return f"{super().__str__()}\nServer ID: {self.server_id}, role name: {self.role_name}"
