from datetime import datetime

from multidict import CIMultiDict

from .header_utils import try_get_retry_after
from .http_status_error import HttpStatusError

class TooManyRequestsError(HttpStatusError):
    STATUS_CODE: int = 429

    def __init__(self, retry_after: datetime | int | None = None, **attrs):
        super().__init__(TooManyRequestsError.STATUS_CODE, "Too many requests.", **attrs)
        self.retry_after = retry_after

    @property
    def retry_after(self) -> datetime | int | None:
        return self.__retry_after

    @retry_after.setter
    def retry_after(self, value: datetime | int | None) -> None:
        self.__retry_after = value

    @staticmethod
    def from_headers(headers: CIMultiDict) -> 'TooManyRequestsError':
        return TooManyRequestsError(try_get_retry_after(headers))
