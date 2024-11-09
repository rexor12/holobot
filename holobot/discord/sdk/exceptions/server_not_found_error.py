class ServerNotFoundError(Exception):
    @property
    def server_id(self) -> int:
        return self.__server_id

    @server_id.setter
    def server_id(self, value: int) -> None:
        self.__server_id = value

    def __init__(self, server_id: int, *args: object) -> None:
        super().__init__(*args)
        self.server_id = server_id

    def __str__(self) -> str:
        return f"{super().__str__()}\nServer ID: {self.server_id}"
