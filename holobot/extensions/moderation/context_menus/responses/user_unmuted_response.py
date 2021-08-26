from dataclasses import dataclass
from holobot.discord.sdk.context_menus.models import MenuItemResponse

@dataclass
class UserUnmutedResponse(MenuItemResponse):
    author_id: str = ""
    user_id: str = ""