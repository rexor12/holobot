from dataclasses import dataclass, field

from .embed_field import EmbedField
from .embed_footer import EmbedFooter

@dataclass
class Embed:
    title: str | None = None
    description: str | None = None
    color: int | None = 0xEB7D00
    thumbnail_url: str | None = None
    image_url: str | None = None
    fields: list[EmbedField] = field(default_factory=list)
    footer: EmbedFooter | None = None
