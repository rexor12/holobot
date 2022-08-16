def join(value: tuple[str, ...], separator: str = ""):
    return separator.join(value)

def try_parse_int(value: str | None) -> int | None:
    if value is None:
        return None

    try:
        return int(value)
    except ValueError:
        return None

def try_parse_float(value: str | None) -> float | None:
    if value is None:
        return None

    try:
        return float(value)
    except ValueError:
        return None
