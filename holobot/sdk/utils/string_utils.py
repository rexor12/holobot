def join(value: tuple[str, ...], separator: str = ""):
    return separator.join(value)

def try_parse_int(value: str | None) -> int | None:
    try:
        return int(value) if value else None
    except ValueError:
        return None

def try_parse_float(value: str | None) -> float | None:
    try:
        return float(value) if value else None
    except ValueError:
        return None
