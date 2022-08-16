from dataclasses import dataclass

@dataclass(kw_only=True)
class ComboBoxItem:
    text: str
    value: str
    description: str | None = None
