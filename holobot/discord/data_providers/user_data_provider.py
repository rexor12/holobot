from collections.abc import AsyncIterable, Iterable

import hikari

from holobot.discord.bot import get_bot
from holobot.discord.sdk.data_providers import IUserDataProvider
from holobot.discord.sdk.models import UserData
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none

@injectable(IUserDataProvider)
class UserDataProvider(IUserDataProvider):
    async def get_user_data_by_id(
        self,
        user_id: int,
        use_cache: bool = True
    ) -> UserData:
        assert_not_none(user_id, "user_id")

        return await UserDataProvider.__safe_get_user_data_by_id(user_id, use_cache)

    async def get_user_data_by_ids(
        self,
        user_ids: Iterable[int]
    ) -> AsyncIterable[UserData]:
        assert_not_none(user_ids, "user_ids")

        for user_id in user_ids:
            user = await get_bot().get_user_by_id(user_id, True)
            yield UserDataProvider.__transform_user_dto(user)

    async def get_user_data_by_name(
        self,
        server_id: int,
        user_name: str,
        use_cache: bool = True
    ) -> UserData:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_name, "user_name")

        member = await get_bot().get_guild_member_by_name(server_id, user_name, True)
        return await UserDataProvider.__safe_get_user_data_by_id(member.id, use_cache)

    def get_self(self) -> UserData:
        if not (bot_info := get_bot().get_me()):
            raise InvalidOperationError("Self information is not available.")

        return UserDataProvider.__transform_user_dto(bot_info)

    @staticmethod
    def __transform_user_dto(user: hikari.User) -> UserData:
        bot_user = get_bot().get_me()
        avatar_url_small = user.make_avatar_url(size=128)
        return UserData(
            user_id=user.id,
            avatar_url=user.avatar_url and user.avatar_url.url,
            avatar_url_small=avatar_url_small and avatar_url_small.url,
            banner_url=user.banner_url and user.banner_url.url,
            is_self=user == bot_user,
            is_bot=user.is_bot,
            name=user.username
        )

    @staticmethod
    async def __safe_get_user_data_by_id(
        user_id: hikari.Snowflakeish,
        use_cache: bool
    ) -> UserData:
        user = await get_bot().get_user_by_id(user_id, use_cache)
        return UserDataProvider.__transform_user_dto(user)
