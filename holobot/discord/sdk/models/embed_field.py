from dataclasses import dataclass

@dataclass
class EmbedField:
    name: str
    value: str
    is_inline: bool = True
