from holobot.extensions.general.models.user_profiles import ReputationChangeInfo, UserProfile
from holobot.extensions.general.providers import IReputationDataProvider
from holobot.extensions.general.repositories.user_profiles import IUserProfileRepository
from holobot.sdk.ioc.decorators import injectable
from .iuser_profile_manager import IUserProfileManager

@injectable(IUserProfileManager)
class UserProfileManager(IUserProfileManager):
    def __init__(
        self,
        reputation_data_provider: IReputationDataProvider,
        user_profile_repository: IUserProfileRepository
    ) -> None:
        super().__init__()
        self.__reputation_data_provider = reputation_data_provider
        self.__user_profile_repository = user_profile_repository

    async def add_reputation_point(
        self,
        user_id: str
    ) -> ReputationChangeInfo:
        user_profile = await self.__user_profile_repository.get(user_id)
        if user_profile:
            user_profile.reputation_points += 1
            await self.__user_profile_repository.update(user_profile)
            return ReputationChangeInfo(
                reputation_points=user_profile.reputation_points,
                last_custom_background=self.__reputation_data_provider.get_last_unlocked_custom_background(
                    user_profile.reputation_points
                )
            )

        user_profile = UserProfile(
            identifier=user_id,
            reputation_points=1
        )
        await self.__user_profile_repository.add(user_profile)

        return ReputationChangeInfo(
            reputation_points=1,
            last_custom_background=self.__reputation_data_provider.get_last_unlocked_custom_background(1)
        )
