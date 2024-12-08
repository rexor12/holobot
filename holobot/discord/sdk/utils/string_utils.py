import re

_ESCAPE_PATTERN = r"([*_|~<>`\\\[\]])"

def escape_user_text(value: str) -> str:
    return re.sub(_ESCAPE_PATTERN, r"\\\1", value)
