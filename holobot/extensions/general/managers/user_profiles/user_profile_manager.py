from holobot.extensions.general.models.items import BackgroundItem, UserItem
from holobot.extensions.general.models.user_profiles import (
    CustomBackgroundInfo, ReputationChangeInfo, UserProfile
)
from holobot.extensions.general.providers import IReputationDataProvider
from holobot.extensions.general.repositories import IUserItemRepository
from holobot.extensions.general.repositories.user_profiles import (
    IUserProfileBackgroundRepository, IUserProfileRepository
)
from holobot.extensions.general.sdk.items.models import UserItemId
from holobot.sdk.identification import IHoloflakeProvider
from holobot.sdk.ioc.decorators import injectable
from .iuser_profile_manager import IUserProfileManager

@injectable(IUserProfileManager)
class UserProfileManager(IUserProfileManager):
    def __init__(
        self,
        holoflake_provider: IHoloflakeProvider,
        reputation_data_provider: IReputationDataProvider,
        user_item_repository: IUserItemRepository,
        user_profile_background_repository: IUserProfileBackgroundRepository,
        user_profile_repository: IUserProfileRepository,
    ) -> None:
        super().__init__()
        self.__holoflake_provider = holoflake_provider
        self.__reputation_data_provider = reputation_data_provider
        self.__user_item_repository = user_item_repository
        self.__user_profile_background_repository = user_profile_background_repository
        self.__user_profile_repository = user_profile_repository

    async def add_reputation_point(
        self,
        user_id: int
    ) -> ReputationChangeInfo:
        user_profile = await self.__user_profile_repository.get(user_id)
        if user_profile:
            user_profile.reputation_points += 1
            await self.__user_profile_repository.update(user_profile)

            last_background = self.__reputation_data_provider.get_last_unlocked_background(
                user_profile.reputation_points
            )
            await self.__try_grant_background(user_id, last_background)

            return ReputationChangeInfo(
                reputation_points=user_profile.reputation_points,
                last_custom_background=last_background
            )

        user_profile = UserProfile(
            identifier=user_id,
            reputation_points=1
        )
        await self.__user_profile_repository.add(user_profile)

        last_background = self.__reputation_data_provider.get_last_unlocked_background(1)
        await self.__try_grant_background(user_id, last_background)

        return ReputationChangeInfo(
            reputation_points=1,
            last_custom_background=last_background
        )

    async def get_or_create(self, user_id: int) -> UserProfile:
        user_profile = await self.__user_profile_repository.get(user_id)
        if user_profile:
            return user_profile

        user_profile = UserProfile(identifier=user_id)
        await self.__user_profile_repository.add(user_profile)

        return user_profile

    async def __try_grant_background(
        self,
        user_id: int,
        last_background: CustomBackgroundInfo | None
    ) -> None:
        if not last_background:
            return

        background_id = await self.__user_profile_background_repository.get_id_by_code(
            last_background.code
        )
        if not background_id:
            return

        if await self.__user_item_repository.background_exists(
            user_id,
            background_id
        ):
            return

        await self.__user_item_repository.add(UserItem(
            identifier=UserItemId(
                server_id=0,
                user_id=user_id,
                serial_id=self.__holoflake_provider.get_next_id()
            ),
            item=BackgroundItem(
                count=1,
                background_id=background_id
            )
        ))
