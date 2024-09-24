from collections.abc import Awaitable

from holobot.extensions.general.models.user_profiles import RankingInfo, UserProfile
from holobot.extensions.general.sdk.badges.models import BadgeId
from holobot.sdk.database import IDatabaseManager, IUnitOfWorkProvider
from holobot.sdk.database.entities import PrimaryKey
from holobot.sdk.database.queries import Query
from holobot.sdk.database.queries.constraints import (
    and_expression, column_expression, or_expression
)
from holobot.sdk.database.queries.enums import Equality, Order
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.queries import PaginationResult
from .iuser_profile_repository import IUserProfileRepository
from .records import UserProfileRecord

@injectable(IUserProfileRepository)
class UserProfileRepository(
    RepositoryBase[str, UserProfileRecord, UserProfile],
    IUserProfileRepository
):
    @property
    def record_type(self) -> type[UserProfileRecord]:
        return UserProfileRecord

    @property
    def model_type(self) -> type[UserProfile]:
        return UserProfile

    @property
    def identifier_type(self) -> type[str]:
        return str

    @property
    def table_name(self) -> str:
        return "user_profiles"

    def __init__(
        self,
        database_manager: IDatabaseManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__(database_manager, unit_of_work_provider)

    async def paginate_rankings(
        self,
        page_index: int,
        page_size: int
    ) -> PaginationResult[RankingInfo]:
        columns = set[str](("id", "reputation_points"))
        async with (session := await self._get_session()):
            result = await (Query
                .select()
                .columns(*columns)
                .from_table(self.table_name)
                .paginate((("reputation_points", Order.DESCENDING),), page_index, page_size)
                .compile().fetch(session.connection)
            )

            return PaginationResult[RankingInfo](
                result.page_index,
                result.page_size,
                result.total_count,
                [
                    RankingInfo(
                        user_id=record["id"],
                        reputation_points=record["reputation_points"]
                    )
                    for record in result.records
                ]
            )

    def is_badge_equipped(
        self,
        user_id: str,
        badge_id: BadgeId
    ) -> Awaitable[bool]:
        return self._exists_by_filter(
            lambda where: where.expression(and_expression(
                column_expression("id", Equality.EQUAL, user_id),
                or_expression(
                    and_expression(
                        column_expression("badge_id1", Equality.EQUAL, badge_id.badge_id),
                        column_expression("badge_sid1", Equality.EQUAL, badge_id.server_id)
                    ),
                    *[
                        and_expression(
                            column_expression(f"badge_id{index + 2}", Equality.EQUAL, badge_id.badge_id),
                            column_expression(f"badge_sid{index + 2}", Equality.EQUAL, badge_id.server_id)
                        )
                        for index in range(UserProfile.MAX_BADGE_COUNT - 1)
                    ]
                ),
            ))
        )

    def _map_record_to_model(self, record: UserProfileRecord) -> UserProfile:
        model = UserProfile(
            identifier=record.id.value,
            reputation_points=record.reputation_points,
            background_image_code=record.background_image_code,
            show_badges=record.show_badges
        )

        for index, _ in enumerate(model.badges):
            badge_id = getattr(record, f"badge_id{index + 1}", None)
            server_id = getattr(record, f"badge_sid{index + 1}", None)
            if badge_id is not None and server_id is not None:
                model.badges.set_item(index, BadgeId(server_id=server_id, badge_id=badge_id))

        return model

    def _map_model_to_record(self, model: UserProfile) -> UserProfileRecord:
        record = UserProfileRecord(
            id=PrimaryKey(model.identifier),
            reputation_points=model.reputation_points,
            background_image_code=model.background_image_code,
            show_badges=model.show_badges
        )

        for index, badge in enumerate(model.badges):
            if badge is None:
                continue

            setattr(record, f"badge_id{index + 1}", badge.badge_id)
            setattr(record, f"badge_sid{index + 1}", badge.server_id)

        return record
