from .header_utils import try_get_retry_after
from .http_status_error import HttpStatusError
from datetime import datetime
from multidict import CIMultiDict
from typing import Optional, Union

class ImATeapotError(HttpStatusError):
    STATUS_CODE: int = 418

    def __init__(self, retry_after: Optional[Union[datetime, int]] = None, **attrs):
        super().__init__(ImATeapotError.STATUS_CODE, "I'm a teapot.", **attrs)
        self.retry_after = retry_after

    @property
    def retry_after(self) -> Optional[Union[datetime, int]]:
        return self.__retry_after
    
    @retry_after.setter
    def retry_after(self, value: Optional[Union[datetime, int]]) -> None:
        self.__retry_after = value
    
    @staticmethod
    def from_headers(headers: CIMultiDict) -> 'ImATeapotError':
        return ImATeapotError(try_get_retry_after(headers))
