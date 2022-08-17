def join(value: tuple[str, ...], separator: str = ""):
    return separator.join(value)

def rank_match(pattern: str, value: str) -> int:
    relevance = 0
    pattern_lower = pattern.lower()
    value_lower = value.lower()

    # Containment, different casing.
    if pattern_lower not in value_lower:
        return relevance
    relevance += 1

    # Full match, different casing.
    if pattern_lower == value_lower:
        relevance += 1

    # Containment, same casing.
    if pattern not in value:
        return relevance
    relevance += 1

    # Full match, same casing.
    if pattern != value:
        return relevance

    return relevance + 1

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
