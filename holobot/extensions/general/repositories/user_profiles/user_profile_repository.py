from holobot.extensions.general.models.user_profiles import RankingInfo, UserProfile
from holobot.sdk.database import IDatabaseManager, IUnitOfWorkProvider
from holobot.sdk.database.entities import PrimaryKey
from holobot.sdk.database.queries import Query
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

    def _map_record_to_model(self, record: UserProfileRecord) -> UserProfile:
        return UserProfile(
            identifier=record.id.value,
            reputation_points=record.reputation_points,
            background_image_code=record.background_image_code
        )

    def _map_model_to_record(self, model: UserProfile) -> UserProfileRecord:
        return UserProfileRecord(
            id=PrimaryKey(model.identifier),
            reputation_points=model.reputation_points,
            background_image_code=model.background_image_code
        )
