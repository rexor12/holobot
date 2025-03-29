class CurrencyNotFoundException(Exception):
    @property
    def currency_id(self) -> int:
        return self.__currency_id

    def __init__(
        self,
        currency_id: int,
        message: str | None = None
    ) -> None:
        super().__init__(message)
        self.__currency_id = currency_id
