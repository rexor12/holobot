from dataclasses import dataclass

@dataclass(kw_only=True, frozen=True)
class UserData:
    user_id: int
    avatar_url: str | None
    # TODO Refactor this so that URLs are generated on request.
    avatar_url_small: str | None
    banner_url: str | None
    name: str
    is_self: bool
    is_bot: bool
