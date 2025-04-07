from dataclasses import dataclass

@dataclass(kw_only=True, frozen=True)
class MemberData:
    user_id: int
    avatar_url: str | None
    server_specific_avatar_url: str | None
    banner_url: str | None
    server_specific_banner_url: str | None
    name: str
    nick_name: str | None
    is_self: bool
    is_bot: bool
    color: int | None

    @property
    def display_name(self) -> str:
        return self.nick_name or self.name

    @property
    def dominant_avatar_url(self) -> str | None:
        return self.server_specific_avatar_url or self.avatar_url

    @property
    def dominant_banner_url(self) -> str | None:
        return self.server_specific_banner_url or self.banner_url
