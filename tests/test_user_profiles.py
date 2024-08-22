import os
from collections.abc import Sequence

from holobot.extensions.general.factories import UserProfileFactory
from holobot.extensions.general.models.user_profiles import (
    CustomBackgroundInfo, ReputationRankInfo, UserProfile
)
from holobot.extensions.general.options import UserProfileOptions
from holobot.extensions.general.providers import IReputationDataProvider
from holobot.extensions.general.sdk.badges.models import BadgeId
from holobot.sdk.configs import IOptions
from tests.machinery import TestEnvironment, TestI18nProvider, TestLoggerFactory

class TestOptionsProvider(IOptions[UserProfileOptions]):
    @property
    def value(self) -> UserProfileOptions:
        return UserProfileOptions()

class TestReputationDataProvider(IReputationDataProvider):
    def get_rank_info(self, reputation_points: int) -> ReputationRankInfo:
        return ReputationRankInfo(
            current_rank=2,
            last_required=30,
            next_required=50,
            color=(155, 0, 0)
        )

    def get_custom_backgrounds(self) -> Sequence[CustomBackgroundInfo]:
        return (
            CustomBackgroundInfo(code="3", required_reputation=30, file_name="3.png"),
        )

    def get_last_unlocked_custom_background(
        self,
        reputation_points: int
    ) -> CustomBackgroundInfo | None:
        raise NotImplementedError

    def is_custom_background_unlocked(self, code: str, reputation_points: int) -> bool:
        raise NotImplementedError

    def get_custom_background(self, index: int) -> CustomBackgroundInfo | None:
        raise NotImplementedError

    def get_custom_background_by_code(self, code: str) -> CustomBackgroundInfo | None:
        raise NotImplementedError

# Set up test environment
environment = TestEnvironment()
i18n_provider = TestI18nProvider()
logger_factory = TestLoggerFactory()
options = TestOptionsProvider()
factory = UserProfileFactory(
    environment=environment,
    i18n_provider=i18n_provider,
    logger_factory=logger_factory,
    options=options,
    reputation_data_provider=TestReputationDataProvider()
)

# Generate a profile image
user_profile = UserProfile(
    identifier="401490060156862466",
    reputation_points=37,
    background_image_code="3"
)
user_profile.badges.set_item(1, BadgeId(server_id="0", badge_id=0))
user_profile.badges.set_item(2, BadgeId(server_id="0", badge_id=1))
user_profile.badges.set_item(4, BadgeId(server_id="0", badge_id=9000))

profile_image = factory.create_profile_image(
    "Test User Name",
    user_profile=user_profile,
    avatar=None,
    custom_background_code=None
)

file_path = os.path.join(environment.root_path, ".test", "user_profile.png")
print(f"[TEST] Writing user profile image to '{file_path}'...")
with (f := open(file_path, "wb")):
    f.write(profile_image)
    f.flush()

print(f"[TEST] User profile image written to '{file_path}'")
