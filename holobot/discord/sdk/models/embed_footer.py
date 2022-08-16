from dataclasses import dataclass

@dataclass
class EmbedFooter:
    text: str | None = None
    icon_url: str | None = None
