from dataclasses import dataclass, field
from typing import Any

@dataclass(kw_only=True)
class QuestRewardBase:
    count: int
    extension_data: dict[str, Any] = field(default_factory=dict)
