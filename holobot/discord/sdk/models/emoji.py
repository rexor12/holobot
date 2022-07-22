from dataclasses import dataclass
from typing import Optional

@dataclass(kw_only=True)
class Emoji:
    identifier: Optional[str]
    url: Optional[str]
    mention: Optional[str]
    is_known: bool
