class AlreadyMarriedError(Exception):
    @property
    def user_id1(self) -> str:
        return self.__user_id1

    @user_id1.setter
    def user_id1(self, value: str) -> None:
        self.__user_id1 = value

    @property
    def user_id2(self) -> str:
        return self.__user_id2

    @user_id2.setter
    def user_id2(self, value: str) -> None:
        self.__user_id2 = value

    def __init__(self, user_id1: str, user_id2: str, *args: object) -> None:
        super().__init__(*args)
        self.user_id1 = user_id1
        self.user_id2 = user_id2

    def __str__(self) -> str:
        return f"{super().__str__()}\nUser ID 1: {self.user_id1}, user ID 2: {self.user_id2}"
