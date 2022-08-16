from dataclasses import dataclass

@dataclass(kw_only=True)
class Emoji:
    identifier: str | None
    url: str | None
    mention: str | None
    is_known: bool
