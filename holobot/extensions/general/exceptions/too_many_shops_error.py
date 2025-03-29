class TooManyShopsError(Exception):
    @property
    def shop_count(self) -> int:
        return self.__shop_count

    @property
    def shop_count_max(self) -> int:
        return self.__shop_count_max

    def __init__(
        self,
        shop_count: int,
        shop_count_max: int,
        message: str | None = None
    ) -> None:
        super().__init__(message)
        self.__shop_count = shop_count
        self.__shop_count_max = shop_count_max
