from dataclasses import dataclass

@dataclass(kw_only=True)
class ComponentBase:
    id: str
