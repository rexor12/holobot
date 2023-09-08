from datetime import timedelta

class RateLimitedError(Exception):
    @property
    def retry_after(self) -> timedelta:
        return self.__retry_after

    @retry_after.setter
    def retry_after(self, value: timedelta) -> None:
        self.__retry_after = value

    def __init__(
        self,
        retry_after: timedelta,
        *args: object
    ) -> None:
        super().__init__(*args)
        self.retry_after = retry_after

    def __str__(self) -> str:
        return f"{super().__str__()}\nRetry after: {self.retry_after}"
