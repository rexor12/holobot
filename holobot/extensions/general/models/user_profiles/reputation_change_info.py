from dataclasses import dataclass

from .custom_background_info import CustomBackgroundInfo

@dataclass(kw_only=True, frozen=True)
class ReputationChangeInfo:
    reputation_points: int
    last_custom_background: CustomBackgroundInfo | None
