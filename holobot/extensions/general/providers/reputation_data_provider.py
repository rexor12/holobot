from typing import cast

from PIL import ImageColor

from holobot.extensions.general.models.user_profiles import CustomBackgroundInfo, ReputationRankInfo
from holobot.extensions.general.options import UserProfileOptions
from holobot.sdk.configs import IOptions
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils.list_utils import binary_search_lower
from .ireputation_data_provider import IReputationDataProvider

@injectable(IReputationDataProvider)
class ReputationDataProvider(IReputationDataProvider):
    def __init__(
        self,
        options: IOptions[UserProfileOptions]
    ) -> None:
        super().__init__()
        self.__rank_infos = sorted(
            map(
                lambda i: (
                    i.RequiredReputation,
                    # It's always tuple[int, ...] for the RGBA color mode.
                    cast(tuple[int, ...], ImageColor.getcolor(i.Color, "RGBA"))
                ),
                options.value.ReputationTable
            ),
            key=lambda i: i[0]
        )
        self.__custom_background_infos = sorted(
            map(
                lambda i: CustomBackgroundInfo(
                    code=i.Code,
                    required_reputation=i.RequiredReputation
                ),
                options.value.CustomBackgrounds
            ),
            key=lambda i: i.required_reputation
        )

    def get_rank_info(self, reputation_points: int) -> ReputationRankInfo:
        current_rank = binary_search_lower(self.__rank_infos, lambda i: i[0], reputation_points)

        return ReputationRankInfo(
            current_rank=current_rank,
            next_required=(
                1
                if current_rank >= len(self.__rank_infos) - 1
                else self.__rank_infos[current_rank + 1][0]
            ),
            last_required=(
                0
                if current_rank <= 0
                else self.__rank_infos[current_rank][0]
            ),
            color=(
                self.__rank_infos[len(self.__rank_infos) - 1][1]
                if current_rank >= len(self.__rank_infos) - 1
                else self.__rank_infos[current_rank][1]
            )
        )

    def get_last_unlocked_background(
        self,
        reputation_points: int
    ) -> CustomBackgroundInfo | None:
        index = binary_search_lower(
            self.__custom_background_infos,
            lambda i: i.required_reputation,
            reputation_points
        )

        if index == -1:
            return None

        custom_background_info = self.__custom_background_infos[index]

        return (
            custom_background_info
            if custom_background_info.required_reputation <= reputation_points
            else None
        )
