from dataclasses import dataclass

@dataclass
class MemberData:
    user_id: str = ""
    avatar_url: str = ""
    name: str = ""
    nick_name: str = ""

    @property
    def display_name(self) -> str:
        return self.nick_name if self.nick_name else self.name
