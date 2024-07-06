class CurrencyNotFoundException(Exception):
    @property
    def currency_id(self) -> int:
        return self.__currency_id

    @property
    def server_id(self) -> str | None:
        return self.__server_id

    def __init__(
        self,
        currency_id: int,
        server_id: str | None,
        message: str | None = None
    ) -> None:
        super().__init__(message)
        self.__currency_id = currency_id
        self.__server_id = server_id
