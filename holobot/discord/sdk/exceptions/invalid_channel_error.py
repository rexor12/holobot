class InvalidChannelError(Exception):
    def __init__(self, server_id: str | None, channel_id: str, *args: object) -> None:
        super().__init__(*args)
        self.__server_id = server_id
        self.__channel_id = channel_id
    
    @property
    def channel_id(self) -> str:
        return self.__channel_id
