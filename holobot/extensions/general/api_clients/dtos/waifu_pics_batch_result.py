from dataclasses import dataclass, field

@dataclass
class WaifuPicsBatchResult:
    files: list[str] = field(default_factory=list)
