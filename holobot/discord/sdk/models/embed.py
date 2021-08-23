from .embed_field import EmbedField
from .embed_footer import EmbedFooter
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Embed:
    title: str = ""
    description: str = ""
    color: int = 0xEB7D00
    thumbnail_url: Optional[str] = None
    fields: List[EmbedField] = []
    footer: Optional[EmbedFooter] = None
