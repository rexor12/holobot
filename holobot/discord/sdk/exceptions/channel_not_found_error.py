class ChannelNotFoundError(Exception):
    def __init__(self, channel_id: str, server_id: str | None = None, *args: object) -> None:
        super().__init__(*args)
        self.__server_id: str | None = server_id
        self.__channel_id: str = channel_id

    @property
    def server_id(self) -> str | None:
        return self.__server_id

    @property
    def channel_id(self) -> str:
        return self.__channel_id

    def __str__(self) -> str:
        return f"{super().__str__()}\nServer ID: {self.server_id}, channel ID: {self.channel_id}"
