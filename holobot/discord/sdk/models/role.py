from dataclasses import dataclass

@dataclass
class Role:
    id: int
    name: str
    description: str | None = None
