from dataclasses import dataclass

@dataclass
class MemberData:
    user_id: str
    avatar_url: str | None
    name: str
    nick_name: str | None
    is_self: bool
    is_bot: bool

    @property
    def display_name(self) -> str:
        return self.nick_name or self.name
