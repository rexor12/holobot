from collections.abc import Sequence
from typing import Protocol

from holobot.extensions.general.models.user_profiles import CustomBackgroundInfo, ReputationRankInfo

class IReputationDataProvider(Protocol):
    def get_rank_info(self, reputation_points: int) -> ReputationRankInfo:
        ...

    def get_custom_backgrounds(self) -> Sequence[CustomBackgroundInfo]:
        ...

    def get_last_unlocked_custom_background(
        self,
        reputation_points: int
    ) -> CustomBackgroundInfo | None:
        ...

    def is_custom_background_unlocked(self, code: str, reputation_points: int) -> bool:
        ...

    def get_custom_background(self, index: int) -> CustomBackgroundInfo | None:
        ...

    def get_custom_background_by_code(self, code: str) -> CustomBackgroundInfo | None:
        ...
