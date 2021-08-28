class RoleAlreadyExistsError(Exception):
    def __init__(self, server_id: str, role_name: str, *args: object) -> None:
        super().__init__(*args)
        self.__server_id: str = server_id
        self.__role_name: str = role_name

    @property
    def server_id(self) -> str:
        return self.__server_id

    @property
    def role_name(self) -> str:
        return self.__role_name
