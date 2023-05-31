import re

ESCAPE_REGEX = re.compile(r"([\[\]\(\)*_~<>])")

def escape_user_input(value: str) -> str:
    return ESCAPE_REGEX.sub(lambda m: f"\\{m.group(0)}", value)
