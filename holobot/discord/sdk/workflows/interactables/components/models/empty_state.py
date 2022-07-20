from dataclasses import dataclass

@dataclass
class EmptyState:
    pass

DEFAULT_EMPTY_STATE: EmptyState = EmptyState()
