class AlreadyMarriedError(Exception):
    def __init__(self, user_id1: str, user_id2: str, *args: object) -> None:
        super().__init__(*args)
        self.__user_id1 = user_id1
        self.__user_id2 = user_id2

    @property
    def user_id1(self) -> str:
        return self.__user_id1

    @property
    def user_id2(self) -> str:
        return self.__user_id2
