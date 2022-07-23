from dataclasses import dataclass
from typing import Optional

@dataclass(kw_only=True)
class ComboBoxItem:
    text: str
    value: str
    description: Optional[str] = None
