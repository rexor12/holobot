class MessageNotFoundError(Exception):
    def __init__(self, message_id: str, *args: object) -> None:
        super().__init__(*args)
        self.__message_id: str = message_id
    
    @property
    def message_id(self) -> str:
        return self.__message_id
