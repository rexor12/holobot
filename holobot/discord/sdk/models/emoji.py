from dataclasses import dataclass
from typing import Optional

@dataclass
class Emoji:
    identifier: Optional[str]
    url: Optional[str]
    mention: Optional[str]
