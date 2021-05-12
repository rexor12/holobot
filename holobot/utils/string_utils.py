from typing import Tuple

def join(value: Tuple[str, ...], separator: str = ""):
    return separator.join(value)

def try_parse_int(value: str) -> Tuple[bool, int]:
    try:
        return (True, int(value))
    except ValueError:
        return (False, 0)
