from datetime import timedelta

def textify_timedelta(value: timedelta | None) -> str:
    if value is None:
        return "never"

    days, remainder = divmod(value.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    format_parts = []
    __add_non_default(format_parts, days, "day(s)")
    __add_non_default(format_parts, hours, "hour(s)")
    __add_non_default(format_parts, minutes, "minute(s)")
    __add_non_default(format_parts, seconds, "second(s)")
    return " ".join(format_parts)

def __add_non_default(list: list[str], value: float, text: str) -> None:
    if value > 0:
        list.extend((str(int(value)), text))
