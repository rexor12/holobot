from .parsers import try_parse_http_date
from datetime import datetime
from holobot.sdk.utils import try_parse_int
from multidict import CIMultiDict
from typing import Optional, Union

def try_get_retry_after(headers: CIMultiDict) -> Optional[Union[datetime, int]]:
    retry_after = headers.get("Retry-After", None)
    if retry_after is not None:
        if (http_date := try_parse_http_date(retry_after)) is not None:
            retry_after = http_date
        elif (seconds := try_parse_int(retry_after)) is not None:
            retry_after = seconds
    return retry_after
