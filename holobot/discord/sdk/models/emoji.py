from dataclasses import dataclass

@dataclass(kw_only=True)
class Emoji:
    identifier: int | None
    name: str
    url: str | None
    mention: str | None
    is_known: bool
    is_animated: bool
