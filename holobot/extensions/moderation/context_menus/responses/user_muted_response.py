from dataclasses import dataclass
from holobot.discord.sdk.context_menus.models import MenuItemResponse

@dataclass
class UserMutedResponse(MenuItemResponse):
    author_id: str = ""
    user_id: str = ""