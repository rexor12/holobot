from typing import Protocol

from holobot.extensions.general.models.user_profiles import CustomBackgroundInfo, ReputationRankInfo

class IReputationDataProvider(Protocol):
    def get_rank_info(self, reputation_points: int) -> ReputationRankInfo:
        ...

    def get_last_unlocked_background(
        self,
        reputation_points: int
    ) -> CustomBackgroundInfo | None:
        ...
