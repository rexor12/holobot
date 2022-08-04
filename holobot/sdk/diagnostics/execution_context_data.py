from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass
class ExecutionContextData:
    event_name: str
    elapsed_milliseconds: float = -1
    extra_infos: Dict[str, Any] = field(default_factory=dict)
