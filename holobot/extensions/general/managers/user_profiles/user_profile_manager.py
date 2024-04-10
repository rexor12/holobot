from holobot.extensions.general.models.user_profiles import UserProfile
from holobot.extensions.general.repositories.user_profiles import IUserProfileRepository
from holobot.sdk.ioc.decorators import injectable
from .iuser_profile_manager import IUserProfileManager

@injectable(IUserProfileManager)
class UserProfileManager(IUserProfileManager):
    def __init__(
        self,
        user_profile_repository: IUserProfileRepository
    ) -> None:
        super().__init__()
        self.__user_profile_repository = user_profile_repository

    async def add_reputation_point(
        self,
        user_id: str
    ) -> int:
        user_profile = await self.__user_profile_repository.get(user_id)
        if user_profile:
            user_profile.reputation_points += 1
            await self.__user_profile_repository.update(user_profile)
            return user_profile.reputation_points

        user_profile = UserProfile(
            identifier=user_id,
            reputation_points=1
        )
        await self.__user_profile_repository.add(user_profile)

        return 1
