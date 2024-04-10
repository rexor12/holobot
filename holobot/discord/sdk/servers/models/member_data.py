from dataclasses import dataclass

@dataclass(kw_only=True, frozen=True)
class MemberData:
    user_id: str
    avatar_url: str | None
    server_specific_avatar_url: str | None
    name: str
    nick_name: str | None
    is_self: bool
    is_bot: bool
    color: int | None

    @property
    def display_name(self) -> str:
        return self.nick_name or self.name
