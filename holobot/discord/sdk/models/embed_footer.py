from dataclasses import dataclass
from typing import Optional

@dataclass
class EmbedFooter:
    text: Optional[str] = None
    icon_url: Optional[str] = None
