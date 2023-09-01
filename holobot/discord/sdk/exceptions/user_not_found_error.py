class UserNotFoundError(Exception):
    @property
    def user_id(self) -> str:
        return self.__user_id

    @user_id.setter
    def user_id(self, value: str) -> None:
        self.__user_id = value

    def __init__(self, user_id: str, *args: object) -> None:
        super().__init__(*args)
        self.__user_id: str = user_id

    def __str__(self) -> str:
        return f"{super().__str__()}\nUser ID: {self.user_id}"
