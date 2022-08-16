from dataclasses import dataclass, field
from typing import Any

@dataclass
class ExecutionContextData:
    event_name: str
    elapsed_milliseconds: float = -1
    extra_infos: dict[str, Any] = field(default_factory=dict)
