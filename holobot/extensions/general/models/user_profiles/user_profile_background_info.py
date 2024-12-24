from dataclasses import dataclass

@dataclass(kw_only=True)
class UserProfileBackgroundInfo:
    code: str
    name: str
