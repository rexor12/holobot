from dataclasses import dataclass, field
from holobot.discord.sdk.components import Layout
from typing import Any, Dict

@dataclass
class Paginator(Layout):
    current_page: int = 0
    custom_data: Dict[str, Any] = field(default_factory=dict)
