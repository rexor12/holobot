class ServerNotFoundError(Exception):
    def __init__(self, server_id: str, *args: object) -> None:
        super().__init__(*args)
        self.__server_id: str = server_id
    
    @property
    def server_id(self) -> str:
        return self.__server_id
