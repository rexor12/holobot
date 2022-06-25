from dataclasses import dataclass
from holobot.discord.sdk.components import Layout

@dataclass
class Paginator(Layout):
    current_page: int = 0
