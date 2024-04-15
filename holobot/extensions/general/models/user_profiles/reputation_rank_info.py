from dataclasses import dataclass

@dataclass(kw_only=True, frozen=True)
class ReputationRankInfo:
    current_rank: int
    last_required: int
    next_required: int
    color: tuple[int, ...]
