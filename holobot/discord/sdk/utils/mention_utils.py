import re
from collections.abc import Callable
from typing import TypeVar

mention_regex = re.compile(r"^<@!?(?P<id>\d+)>$")
channel_regex = re.compile(r"^<#(?P<id>\d+)>$")

T = TypeVar("T")

def get_channel_id(mention: str) -> int | None:
    return __match_or_default(
        channel_regex,
        mention,
        "id",
        int
    )

def get_channel_id_or_default(mention: str, default_value: int) -> int:
    return __match(
        channel_regex,
        mention,
        "id",
        int,
        default_value
    )

def get_user_id(mention: str, default_value: int | None = None) -> int | None:
    return __match_or_default(mention_regex, mention, "id", int, default_value)

def __match(
    pattern: re.Pattern[str],
    value: str,
    group_name: str,
    converter: Callable[[str], T],
    default_value: T
) -> T:
    if (match := pattern.match(value)) is None:
        return default_value
    return converter(match.group(group_name))

def __match_or_default(
    pattern: re.Pattern[str],
    value: str,
    group_name: str,
    converter: Callable[[str], T],
    default_value: T | None = None
) -> T | None:
    if (match := pattern.match(value)) is None:
        return default_value
    return converter(match.group(group_name))
