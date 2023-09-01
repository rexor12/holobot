class AuthorizationError(Exception):
    @property
    def user_id(self) -> int:
        return self.__user_id

    @user_id.setter
    def user_id(self, value: int) -> None:
        self.__user_id = value

    def __init__(self, user_id: int):
        super().__init__(f"Unauthorized access from the user with the identifier '{user_id}'.")
        self.user_id = user_id

    def __str__(self) -> str:
        return f"{super().__str__()}\nUser ID: {self.user_id}"
