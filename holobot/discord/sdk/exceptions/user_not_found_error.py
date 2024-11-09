class UserNotFoundError(Exception):
    @property
    def user_id(self) -> int | None:
        return self.__user_id

    @user_id.setter
    def user_id(self, value: int | None) -> None:
        self.__user_id = value

    @property
    def user_name(self) -> str | None:
        return self.__user_name

    @user_name.setter
    def user_name(self, value: str | None) -> None:
        self.__user_name = value

    def __init__(self, user_id: int | None, user_name: str | None, *args: object) -> None:
        super().__init__(*args)
        self.__user_id = user_id
        self.__user_name = user_name

    def __str__(self) -> str:
        return f"{super().__str__()}\nUser ID: {self.user_id}"
