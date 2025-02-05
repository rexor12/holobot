from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.mudada.models import (
    AggregatedRating, RatingMetadata, Valentine2025Rating, Valentine2025RatingId
)
from holobot.sdk.database.repositories import IRepository
from holobot.sdk.queries import PaginationResult

class IValentine2025RatingRepository(
    IRepository[Valentine2025RatingId, Valentine2025Rating],
    Protocol
):
    def get_aggregated_data(
        self,
        user_id: int
    ) -> Awaitable[AggregatedRating | None]:
        ...

    def paginate_ratings(
        self,
        target_user_id: int,
        page_index: int,
        page_size: int
    ) -> Awaitable[PaginationResult[RatingMetadata]]:
        ...
