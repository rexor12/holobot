from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class PagerState:
    current_page: int
    custom_data: Dict[str, Any]
