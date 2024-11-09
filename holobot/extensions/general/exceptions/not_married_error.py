class NotMarriedError(Exception):
    def __init__(
        self,
        server_id: int,
        user_id: int,
        *args: object
    ) -> None:
        super().__init__(*args)
        self.server_id = server_id
        self.user_id = user_id

    @property
    def server_id(self) -> int:
        return self.__server_id

    @server_id.setter
    def server_id(self, value: int) -> None:
        self.__server_id = value

    @property
    def user_id(self) -> int:
        return self.__user_id

    @user_id.setter
    def user_id(self, value: int) -> None:
        self.__user_id = value

    def __str__(self) -> str:
        return f"{super().__str__()}\nServer ID: {self.server_id}, user ID: {self.user_id}"
