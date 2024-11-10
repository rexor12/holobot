from dataclasses import dataclass

@dataclass(kw_only=True, frozen=True)
class InteractionInfo:
    author_id: int
    name: str
