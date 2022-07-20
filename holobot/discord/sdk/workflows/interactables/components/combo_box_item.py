from dataclasses import dataclass
from typing import Optional

@dataclass
class ComboBoxItem:
    text: str
    value: str
    description: Optional[str] = None
