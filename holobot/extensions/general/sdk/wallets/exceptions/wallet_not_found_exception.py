class WalletNotFoundException(Exception):
    @property
    def user_id(self) -> int:
        return self.__user_id

    @property
    def server_id(self) -> int:
        return self.__server_id

    @property
    def currency_id(self) -> int:
        return self.__currency_id

    def __init__(
        self,
        user_id: int,
        server_id: int,
        currency_id: int,
        message: str | None = None
    ) -> None:
        super().__init__(message)
        self.__user_id = user_id
        self.__server_id = server_id
        self.__currency_id = currency_id
