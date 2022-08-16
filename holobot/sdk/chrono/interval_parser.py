from ..utils import pad_left, try_parse_int
from datetime import timedelta

TIME_PARTS: list[str] = [ "D", "H", "M", "S" ]
FIXED_INTERVALS: dict[str, timedelta] = {
    "WEEK": timedelta(weeks=1),
    "DAY": timedelta(days=1),
    "HOUR": timedelta(hours=1)
}

def parse_interval(value: str) -> timedelta:
    args: dict[str, int] = { part: 0 for part in TIME_PARTS }
    value = value.upper()
    if (fixed_interval := FIXED_INTERVALS.get(value, None)) is not None:
        return fixed_interval

    if ":" in value:
        __parse_delimited_into(value, args)
    else: __parse_denoted_into(value, args)

    return timedelta(days=args["D"], hours=args["H"], minutes=args["M"], seconds=args["S"])

def __parse_delimited_into(value: str, args: dict[str, int]) -> None:
    split_values = value.split(":")
    padded_values = pad_left(split_values, "0", len(TIME_PARTS))
    for index in range(0, len(TIME_PARTS)):
        part_value = try_parse_int(padded_values[index])
        args[TIME_PARTS[index]] = part_value if part_value is not None else 0
    if len(split_values) == 2:
        args["H"] = args["M"]
        args["M"] = args["S"]
        args["S"] = 0

def __parse_denoted_into(value: str, args: dict[str, int]) -> None:
    for time_part in args.keys():
        split_values = value.split(time_part, 1)
        if len(split_values) == 2:
            part_value = try_parse_int(split_values[0])
            args[time_part] = part_value if part_value is not None else 0
            value = split_values[1]
            continue
        value = split_values[0]
