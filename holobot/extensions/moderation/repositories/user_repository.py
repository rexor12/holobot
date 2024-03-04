from collections.abc import Awaitable

from holobot.extensions.moderation.enums import ModeratorPermission
from holobot.extensions.moderation.models import User
from holobot.sdk.database import IDatabaseManager, IUnitOfWorkProvider
from holobot.sdk.database.entities import PrimaryKey
from holobot.sdk.database.queries.enums import Connector, Equality, Order
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.queries import PaginationResult
from holobot.sdk.utils import assert_not_none
from .iuser_repository import IUserRepository
from .records import UserRecord

@injectable(IUserRepository)
class UserRepository(
    RepositoryBase[int, UserRecord, User],
    IUserRepository
):
    @property
    def record_type(self) -> type[UserRecord]:
        return UserRecord

    @property
    def model_type(self) -> type[User]:
        return User

    @property
    def identifier_type(self) -> type[int]:
        return int

    @property
    def table_name(self) -> str:
        return "moderation_users"

    def __init__(
        self,
        database_manager: IDatabaseManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__(database_manager, unit_of_work_provider)

    def get_by_server(
        self,
        server_id: str,
        user_id: str
    ) -> Awaitable[User | None]:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        return self._get_by_filter(lambda where: (
            where.fields(
                Connector.AND,
                ("server_id", Equality.EQUAL, server_id),
                ("user_id", Equality.EQUAL, user_id)
            )
        ))

    def delete_by_server(
        self,
        server_id: str,
        user_id: str
    ) -> Awaitable[int]:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        return self._delete_by_filter(
            lambda where: where.fields(
                Connector.AND,
                ("server_id", Equality.EQUAL, server_id),
                ("user_id", Equality.EQUAL, user_id)
            )
        )

    def get_moderators(
        self,
        server_id: str,
        page_index: int,
        page_size: int
    ) -> Awaitable[PaginationResult[User]]:
        assert_not_none(server_id, "server_id")

        return self._paginate(
            (("id", Order.ASCENDING),),
            page_index,
            page_size,
            lambda where: where.fields(
                Connector.AND,
                ("server_id", Equality.EQUAL, server_id),
                ("permissions", Equality.GREATER, ModeratorPermission.NONE)
            )
        )

    def _map_record_to_model(self, record: UserRecord) -> User:
        return User(
            identifier=record.id.value,
            created_at=record.created_at,
            permissions=record.permissions,
            server_id=record.server_id,
            user_id=record.user_id
        )

    def _map_model_to_record(self, model: User) -> UserRecord:
        return UserRecord(
            id=PrimaryKey(model.identifier),
            created_at=model.created_at,
            permissions=model.permissions,
            server_id=model.server_id,
            user_id=model.user_id
        )
