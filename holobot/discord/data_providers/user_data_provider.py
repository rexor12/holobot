import hikari

from holobot.discord.bot import BotAccessor
from holobot.discord.sdk.data_providers import IUserDataProvider
from holobot.discord.sdk.exceptions import UserNotFoundError
from holobot.discord.sdk.models import UserData
from holobot.discord.utils import get_guild_member_by_name
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none

@injectable(IUserDataProvider)
class UserDataProvider(IUserDataProvider):
    async def get_user_data_by_id(
        self,
        user_id: str,
        force_fetch: bool = False
    ) -> UserData:
        assert_not_none(user_id, "user_id")

        user = await UserDataProvider.__get_or_fetch_user(user_id, force_fetch)
        return UserDataProvider.__transform_user_dto(user)

    async def get_user_data_by_name(
        self,
        server_id: str,
        user_name: str,
        force_fetch: bool = False
    ) -> UserData:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_name, "user_name")

        member = get_guild_member_by_name(server_id, user_name)
        user = await UserDataProvider.__get_or_fetch_user(str(member.id), force_fetch)
        return UserDataProvider.__transform_user_dto(user)

    @staticmethod
    async def __get_or_fetch_user(user_id: str, force_fetch: bool) -> hikari.User:
        bot = BotAccessor.get_bot()
        if not force_fetch and (user := bot.cache.get_user(int(user_id))):
            return user

        try:
            return await bot.rest.fetch_user(int(user_id))
        except hikari.NotFoundError as error:
            raise UserNotFoundError(user_id) from error

    @staticmethod
    def __transform_user_dto(user: hikari.User) -> UserData:
        bot_user = BotAccessor.get_bot().get_me()
        return UserData(
            user_id=str(user.id),
            avatar_url=user.avatar_url and user.avatar_url.url,
            banner_url=user.banner_url and user.banner_url.url,
            is_self=user == bot_user,
            is_bot=user.is_bot,
            name=user.username
        )
