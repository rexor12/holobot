from datetime import timedelta
from enum import IntEnum, unique
from holobot.utils.string_utils import try_parse_int
from typing import Dict, List

TIME_PARTS: List[str] = [ "D", "H", "M", "S" ]
FIXED_INTERVALS: Dict[str, timedelta] = {
    "WEEK": timedelta(weeks=1),
    "DAY": timedelta(days=1),
    "HOUR": timedelta(hours=1)
}

@unique
class ParserState(IntEnum):
    PARSING_VALUE = 0,
    PARSING_KEY = 1

class State:
    def __init__(self) -> None:
        self.args: Dict[str, int] = {}
        self.state: ParserState = ParserState.PARSING_VALUE
        self.buffer: str = ""
        self.last_value: str = ""

def parse_interval(value: str) -> timedelta:
    args: Dict[str, int] = { part: 0 for part in TIME_PARTS }
    value = value.upper()
    if (fixed_interval := FIXED_INTERVALS.get(value, None)) is not None:
        return fixed_interval
    for time_part in args.keys():
        split_values = value.split(time_part, 1)
        if len(split_values) == 2:
            is_success, part_value = try_parse_int(split_values[0])
            args[time_part] = part_value if is_success else 0
            value = split_values[1]
            continue
        value = split_values[0]
    return timedelta(days=args["D"], hours=args["H"], minutes=args["M"], seconds=args["S"])
