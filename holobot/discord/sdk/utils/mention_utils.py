from typing import Optional, Pattern

import re

mention_regex = re.compile(r"^<@!?(?P<id>\d+)>$")
channel_regex = re.compile(r"^<#(?P<id>\d+)>$")

def get_channel_id(mention: str) -> Optional[str]:
    return __match_or_default(channel_regex, mention, "id")

def get_channel_id_or_default(mention: str, default_value: str) -> str:
    return __match(channel_regex, mention, "id", default_value)

def get_user_id(mention: str, default_value: Optional[str] = None) -> Optional[str]:
    return __match_or_default(mention_regex, mention, "id", default_value)

def __match(pattern: Pattern[str], value: str, group_name: str, default_value: str) -> str:
    if (match := pattern.match(value)) is None:
        return default_value
    return match.group(group_name)

def __match_or_default(pattern: Pattern[str], value: str, group_name: str, default_value: Optional[str] = None) -> Optional[str]:
    if (match := pattern.match(value)) is None:
        return default_value
    return match.group(group_name)
