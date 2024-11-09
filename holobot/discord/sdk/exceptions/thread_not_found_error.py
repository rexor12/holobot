class ThreadNotFoundError(Exception):
    def __init__(self, thread_id: int, server_id: int | None = None, *args: object) -> None:
        super().__init__(*args)
        self.__server_id = server_id
        self.__thread_id = thread_id

    @property
    def server_id(self) -> int | None:
        return self.__server_id

    @property
    def thread_id(self) -> int:
        return self.__thread_id

    def __str__(self) -> str:
        return f"{super().__str__()}\nServer ID: {self.server_id}, thread ID: {self.thread_id}"
