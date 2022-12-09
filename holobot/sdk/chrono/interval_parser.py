import re
from datetime import timedelta

from holobot.sdk.exceptions import ArgumentOutOfRangeError
from holobot.sdk.utils.string_utils import try_parse_int
from .invalid_input_error import InvalidInputError

FIXED_INTERVALS: dict[str, timedelta] = {
    "WEEK": timedelta(weeks=1),
    "DAY": timedelta(days=1),
    "HOUR": timedelta(hours=1)
}
DELIMITED_INPUT_REGEX = re.compile(r"^(?P<high>\d+):(?P<mid>\d+)(?::(?P<low>\d+))?$")
DENOTED_INPUT_REGEX = re.compile(r"^(?:(?P<day>\d+)D)? *(?:(?P<hour>\d+)H)? *(?:(?P<minute>\d+)M)? *(?:(?P<second>\d+)S)?$")

def parse_interval(value: str) -> timedelta:
    value = value.upper()
    if (fixed_interval := FIXED_INTERVALS.get(value)) is not None:
        return fixed_interval

    if ":" in value:
        if not (match := DELIMITED_INPUT_REGEX.match(value)):
            raise InvalidInputError()

        days = "0"
        hours = match["high"]
        minutes = match["mid"]
        seconds = match["low"] if match["low"] else "0"
    else:
        if not (match := DENOTED_INPUT_REGEX.match(value)):
            raise InvalidInputError()

        days = match["day"]
        hours = match["hour"]
        minutes = match["minute"]
        seconds = match["second"]

    return timedelta(
        days=__parse_time_component(days or "0", 0, None),
        hours=__parse_time_component(hours or "0", 0, 23 if days else None),
        minutes=__parse_time_component(minutes or "0", 0, 59 if hours else None),
        seconds=__parse_time_component(seconds or "0", 0, 59 if minutes else None)
    )

def __parse_time_component(value: str, min: int, max: int | None) -> int:
    if (int_value := try_parse_int(value)) is None:
        raise InvalidInputError()

    if int_value < min or (max is not None and int_value > max):
        raise ArgumentOutOfRangeError("value", str(min), str(max))

    return int_value
