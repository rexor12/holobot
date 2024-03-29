from datetime import datetime

from multidict import CIMultiDict

from holobot.sdk.utils import try_parse_int
from .parsers import try_parse_http_date

def try_get_retry_after(headers: CIMultiDict) -> datetime | int | None:
    retry_after = headers.get("Retry-After")
    if retry_after is not None:
        if (http_date := try_parse_http_date(retry_after)) is not None:
            retry_after = http_date
        elif (seconds := try_parse_int(retry_after)) is not None:
            retry_after = seconds
    return retry_after
