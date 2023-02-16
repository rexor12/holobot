class NotMarriedError(Exception):
    def __init__(self, user_id: str, *args: object) -> None:
        super().__init__(*args)
        self.__user_id = user_id

    @property
    def user_id(self) -> str:
        return self.__user_id
