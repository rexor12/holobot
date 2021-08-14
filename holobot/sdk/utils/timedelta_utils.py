from datetime import timedelta
from typing import List, Optional

def textify_timedelta(value: Optional[timedelta]) -> str:
    if value is None:
        return "never"

    days, remainder = divmod(value.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    format_parts = []
    __add_non_default(format_parts, days, "days")
    __add_non_default(format_parts, hours, "hours")
    __add_non_default(format_parts, minutes, "minutes")
    __add_non_default(format_parts, seconds, "seconds")
    return " ".join(format_parts)

def __add_non_default(list: List[str], value: float, text: str) -> None:
    if value <= 0:
        return
    
    list.append(str(int(value)))
    list.append(text)
