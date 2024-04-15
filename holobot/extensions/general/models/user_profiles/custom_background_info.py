from dataclasses import dataclass

@dataclass(kw_only=True, frozen=True)
class CustomBackgroundInfo:
    code: str
    required_reputation: int
    file_name: str
