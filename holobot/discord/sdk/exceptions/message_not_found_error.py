class MessageNotFoundError(Exception):
    def __init__(self, channel_id: str, message_id: str, *args: object) -> None:
        super().__init__(*args)
        self.__channel_id: str = channel_id
        self.__message_id: str = message_id

    @property
    def channel_id(self) -> str:
        return self.__channel_id

    @property
    def message_id(self) -> str:
        return self.__message_id

    def __str__(self) -> str:
        return f"{super().__str__()}\nChannel ID: {self.channel_id}, message ID: {self.message_id}"
