from aiohttp.client_reqrep import ClientResponse
from holobot.network.exceptions.http_status_error import HttpStatusError
from multidict import CIMultiDictProxy
from holobot.network.exceptions.parsers import try_parse_http_date, try_parse_int

class TooManyRequestsError(HttpStatusError):
    STATUS_CODE: int = 429

    def __init__(self, **attrs):
        super().__init__(TooManyRequestsError.STATUS_CODE, "Too many requests.", **attrs)
    
    @staticmethod
    def from_client_response(response: ClientResponse):
        headers: CIMultiDictProxy[str] = response.headers()
        retry_after = headers.get("Retry-After", None)
        if retry_after is not None:
            http_date = try_parse_http_date(retry_after)
            if http_date is not None:
                retry_after = http_date
            else:
                seconds = try_parse_int(retry_after)
                retry_after = seconds if seconds is not None else retry_after
        return TooManyRequestsError(retry_after=retry_after)