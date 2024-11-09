class InvalidChannelError(Exception):
    @property
    def channel_id(self) -> int:
        return self.__channel_id

    @channel_id.setter
    def channel_id(self, value: int) -> None:
        self.__channel_id = value

    @property
    def server_id(self) -> int | None:
        return self.__server_id

    @server_id.setter
    def server_id(self, value: int | None) -> None:
        self.__server_id = value

    def __init__(self, server_id: int | None, channel_id: int, *args: object) -> None:
        super().__init__(*args)
        self.server_id = server_id
        self.channel_id = channel_id

    def __str__(self) -> str:
        return f"{super().__str__()}\nServer ID: {self.server_id}, channel ID: {self.channel_id}"
