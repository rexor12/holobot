class ThreadNotFoundError(Exception):
    def __init__(self, thread_id: str, server_id: str | None = None, *args: object) -> None:
        super().__init__(*args)
        self.__server_id: str | None = server_id
        self.__thread_id: str = thread_id

    @property
    def server_id(self) -> str | None:
        return self.__server_id

    @property
    def thread_id(self) -> str:
        return self.__thread_id

    def __str__(self) -> str:
        return f"{super().__str__()}\nServer ID: {self.server_id}, thread ID: {self.thread_id}"
