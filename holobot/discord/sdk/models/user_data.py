from dataclasses import dataclass

@dataclass(kw_only=True, frozen=True)
class UserData:
    user_id: str
    avatar_url: str | None
    banner_url: str | None
    name: str
    is_self: bool
    is_bot: bool
