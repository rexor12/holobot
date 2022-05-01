from datetime import timedelta
from typing import List, Optional, Tuple

def textify_timedelta(value: Optional[timedelta]) -> str:
    if value is None:
        return "never"
    
    days, hours, minutes, seconds = __get_values(value)
    format_parts = []
    __add_non_default(format_parts, days, "day(s)")
    __add_non_default(format_parts, hours, "hour(s)")
    __add_non_default(format_parts, minutes, "minute(s)")
    __add_non_default(format_parts, seconds, "second(s)")
    return " ".join(format_parts)

def textify_timedelta_short(value: Optional[timedelta]) -> str:
    if value is None:
        return "00:00:00"

    days, hours, minutes, seconds = __get_values(value)
    format_parts = []
    __add_non_default_short(format_parts, days, hide_zero=True)
    __add_non_default_short(format_parts, hours)
    __add_non_default_short(format_parts, minutes)
    __add_non_default_short(format_parts, seconds, False)
    return "".join(format_parts)

def __add_non_default(list: List[str], value: float, text: str) -> None:
    if value <= 0:
        return
    
    list.append(str(int(value)))
    list.append(text)

def __add_non_default_short(list: List[str], value: float, append_colon: bool = True, hide_zero: bool = False) -> None:
    if value <= 0 and hide_zero:
        return
    
    list.append("{:0>2.0f}".format(value))
    if append_colon:
        list.append(":")

def __get_values(value: timedelta) -> Tuple[float, float, float, float]:
    days, remainder = divmod(value.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    return (days, hours, minutes, seconds)
