from dataclasses import dataclass
from typing import Optional

@dataclass
class MemberData:
    user_id: str
    avatar_url: Optional[str]
    name: str
    nick_name: Optional[str]

    @property
    def display_name(self) -> str:
        return self.nick_name or self.name
