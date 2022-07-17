from dataclasses import dataclass, field
from typing import Any, Dict

from .layout import Layout

@dataclass
class Paginator(Layout):
    current_page: int = 0
    custom_data: Dict[str, Any] = field(default_factory=dict)
