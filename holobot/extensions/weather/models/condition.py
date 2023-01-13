from dataclasses import dataclass

@dataclass(kw_only=True)
class Condition:
    identifier: int
    icon: str | None
    condition_image_url: str | None
    description: str | None
