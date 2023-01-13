from dataclasses import dataclass

@dataclass(kw_only=True)
class Wind:
    speed: float | None
    degrees: float | None
