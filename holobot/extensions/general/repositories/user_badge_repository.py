from collections.abc import Awaitable

from holobot.extensions.general.models import UserBadge
from holobot.extensions.general.sdk.badges.models import UserBadgeId
from holobot.sdk.database import IDatabaseManager, IUnitOfWorkProvider
from holobot.sdk.database.entities import PrimaryKey
from holobot.sdk.database.queries.enums import Connector, Equality, Order
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.queries import PaginationResult
from .iuser_badge_repository import IUserBadgeRepository
from .records import UserBadgeRecord

@injectable(IUserBadgeRepository)
class UserBadgeRepository(
    RepositoryBase[UserBadgeId, UserBadgeRecord, UserBadge],
    IUserBadgeRepository
):
    @property
    def record_type(self) -> type[UserBadgeRecord]:
        return UserBadgeRecord

    @property
    def model_type(self) -> type[UserBadge]:
        return UserBadge

    @property
    def identifier_type(self) -> type[UserBadgeId]:
        return UserBadgeId

    @property
    def table_name(self) -> str:
        return "user_badges"

    def __init__(
        self,
        database_manager: IDatabaseManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__(database_manager, unit_of_work_provider)

    def paginate(
        self,
        user_id: int,
        page_index: int,
        page_size: int
    ) -> Awaitable[PaginationResult[UserBadge]]:
        return self._paginate(
            (("badge_id", Order.ASCENDING),),
            page_index,
            page_size,
            lambda where: where.field("user_id", Equality.EQUAL, user_id)
        )

    def exists(self, id: UserBadgeId) -> Awaitable[bool]:
        return self._exists_by_filter(
            lambda where: where.fields(
                Connector.AND,
                ("user_id", Equality.EQUAL, id.user_id),
                ("server_id", Equality.EQUAL, id.server_id),
                ("badge_id", Equality.EQUAL, id.badge_id)
            )
        )

    def _map_record_to_model(self, record: UserBadgeRecord) -> UserBadge:
        return UserBadge(
            identifier=UserBadgeId(
                user_id=record.user_id.value,
                server_id=record.server_id.value,
                badge_id=record.badge_id.value
            ),
            unlocked_at=record.unlocked_at
        )

    def _map_model_to_record(self, model: UserBadge) -> UserBadgeRecord:
        return UserBadgeRecord(
            user_id=PrimaryKey(model.identifier.user_id),
            server_id=PrimaryKey(model.identifier.server_id),
            badge_id=PrimaryKey(model.identifier.badge_id),
            unlocked_at=model.unlocked_at
        )
