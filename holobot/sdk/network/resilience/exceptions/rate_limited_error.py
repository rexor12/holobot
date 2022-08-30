from datetime import timedelta

class RateLimitedError(Exception):
    @property
    def retry_after(self) -> timedelta:
        return self.__retry_after

    def __init__(
        self,
        retry_after: timedelta,
        *args: object
    ) -> None:
        super().__init__(*args)
        self.__retry_after = retry_after
