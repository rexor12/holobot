from typing import Optional, Tuple

def join(value: Tuple[str, ...], separator: str = ""):
    return separator.join(value)

def try_parse_int(value: Optional[str]) -> Optional[int]:
    if value is None:
        return None
    
    try:
        return int(value)
    except ValueError:
        return None

def try_parse_float(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    
    try:
        return float(value)
    except ValueError:
        return None
