from aiohttp.client_reqrep import ClientResponse
from holobot.network.exceptions.http_status_error import HttpStatusError
from multidict import CIMultiDictProxy
from holobot.network.exceptions.parsers import try_parse_http_date, try_parse_int

class ImATeapotError(HttpStatusError):
    STATUS_CODE: int = 418

    def __init__(self, **attrs):
        super().__init__(ImATeapotError.STATUS_CODE, "I'm a teapot.", **attrs)
    
    @staticmethod
    def from_client_response(response: ClientResponse):
        retry_after = response.headers.get("Retry-After", None)
        if retry_after is not None:
            http_date = try_parse_http_date(retry_after)
            if http_date is not None:
                retry_after = http_date
            else:
                seconds = try_parse_int(retry_after)
                retry_after = seconds if seconds is not None else retry_after
        return ImATeapotError(retry_after=retry_after)