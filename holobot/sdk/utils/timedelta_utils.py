from collections.abc import Sequence
from datetime import timedelta

ZERO_TIMEDELTA = timedelta()

__COMPONENT_I18N: tuple[tuple[str, str], ...] = (
    ("days", "day"),
    ("hours", "hour"),
    ("minutes", "minute"),
    ("seconds", "second")
)

def textify_timedelta(
    value: timedelta | None,
    default_text: str = "never",
    only_largest_remaining: bool = False,
    allow_negative_values: bool = False) -> str:
    if value is None:
        return default_text

    days, remainder = divmod(value.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    format_parts = []
    for index, component in enumerate((days, hours, minutes, seconds)):
        i18n = __COMPONENT_I18N[index]
        if (__add_non_default(format_parts, component, i18n[0] if component > 1 else i18n[1], allow_negative_values)
            and only_largest_remaining):
            return __join_parts(format_parts)

    return __join_parts(format_parts) if format_parts else default_text

def __add_non_default(
    items: list[str],
    value: float,
    text: str,
    allow_negative_values: bool = False) -> bool:
    if not value or (not allow_negative_values and value < 0):
        return False

    items.extend((str(int(value)), text))
    return True

def __join_parts(parts: Sequence[str]) -> str:
    return " ".join(parts)
