from collections.abc import Iterable
from datetime import timedelta

from hikari import (
    UNDEFINED as HikariUndefined, BadRequestError as HikariBadRequestError, ChannelFollowerWebhook,
    ChannelType as HikariChannelType, ForbiddenError as HikariForbiddenError, GuildNewsChannel,
    GuildTextChannel, NotFoundError as HikariNotFoundError
)

from holobot.discord.bot import get_bot
from holobot.discord.sdk.exceptions import (
    ChannelNotFoundError, ForbiddenError, InvalidChannelError, ThreadNotFoundError
)
from holobot.discord.sdk.servers.managers import IChannelManager
from holobot.discord.sdk.servers.models import ServerChannel
from holobot.discord.transformers.server_channel import to_model
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none, assert_range

@injectable(IChannelManager)
class ChannelManager(IChannelManager):
    async def get_channels(self, server_id: str) -> Iterable[ServerChannel]:
        assert_not_none(server_id, "server_id")

        guild = await get_bot().get_guild_by_id(int(server_id))
        return list(map(to_model, guild.get_channels().values()))

    async def get_channel_by_id(self, server_id: str, channel_id: str) -> ServerChannel:
        assert_not_none(server_id, "server_id")
        assert_not_none(channel_id, "channel_id")

        channel = await get_bot().get_guild_channel(int(server_id), int(channel_id))

        return to_model(channel)

    async def follow_news_channel(
        self,
        server_id: str,
        channel_id: str,
        source_server_id: str,
        source_channel_id: str
    ) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(channel_id, "channel_id")
        assert_not_none(source_server_id, "source_server_id")
        assert_not_none(source_channel_id, "source_channel_id")

        guild = await get_bot().get_guild_by_id(int(server_id))
        if not (channel := await get_bot().get_guild_channel(guild, int(channel_id))):
            raise ChannelNotFoundError(channel_id)

        source_guild = await get_bot().get_guild_by_id(int(source_server_id))
        if not (source_channel := await get_bot().get_guild_channel(source_guild, int(source_channel_id))):
            raise ChannelNotFoundError(source_channel_id)

        if not isinstance(source_channel, GuildNewsChannel):
            raise InvalidChannelError(
                source_server_id,
                source_channel_id,
                "The source channel must be a news-type channel."
            )

        try:
            await get_bot().rest.follow_channel(source_channel, channel)
        except HikariForbiddenError as error:
            raise ForbiddenError(
                f"Cannot follow news channel '{source_channel.id}' of server '{source_channel.guild_id}' in channel '{channel.id}' of guild '{channel.guild_id}'."
            ) from error
        except HikariBadRequestError as error:
            raise InvalidChannelError(
                server_id,
                channel_id,
                "Cannot follow news channel."
            ) from error

    async def unfollow_news_channel_for_all_channels(
        self,
        server_id: str,
        source_server_id: str,
        source_channel_id: str
    ) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(source_server_id, "source_server_id")
        assert_not_none(source_channel_id, "source_channel_id")

        guild = await get_bot().get_guild_by_id(int(server_id))
        try:
            webhooks = await get_bot().rest.fetch_guild_webhooks(guild)
            for webhook in webhooks:
                if (
                    isinstance(webhook, ChannelFollowerWebhook)
                    and webhook.source_guild
                    and webhook.source_channel
                    and str(webhook.source_guild.id) == source_server_id
                    and str(webhook.source_channel.id) == source_channel_id
                ):
                    await get_bot().rest.delete_webhook(webhook)
        except HikariForbiddenError as error:
            raise ForbiddenError(
                f"Cannot unfollow news channel '{source_channel_id}' of guild '{source_server_id}' in server '{server_id}'."
            ) from error

    async def change_channel_name(self, server_id: str, channel_id: str, name: str) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(channel_id, "channel_id")
        assert_range(len(name), 1, 20, "name")

        channel = await get_bot().get_guild_channel(int(server_id), int(channel_id))

        try:
            await channel.edit(name=name)
        except HikariForbiddenError as error:
            raise ForbiddenError(
                f"Cannot change channel name of channel '{channel_id}' of server '{server_id}'."
            ) from error

    async def create_thread(
        self,
        server_id: str,
        channel_id: str,
        thread_name: str,
        is_private: bool,
        initial_message: str,
        auto_archive_after: timedelta | None = None,
        can_invite_others: bool = True
    ) -> str:
        assert_not_none(server_id, "server_id")
        assert_not_none(channel_id, "channel_id")
        assert_range(len(thread_name), 1, 60, "thread_name")
        assert_not_none(initial_message, "initial_message")

        channel = await get_bot().get_guild_channel(int(server_id), int(channel_id))
        if not isinstance(channel, GuildTextChannel):
            raise InvalidChannelError(server_id, channel_id, "Thread creation is supported for server text channels only.")

        try:
            thread = await get_bot().rest.create_thread(
                channel,
                HikariChannelType.GUILD_PRIVATE_THREAD if is_private else HikariChannelType.GUILD_PUBLIC_THREAD,
                thread_name,
                auto_archive_duration=auto_archive_after or HikariUndefined,
                invitable=can_invite_others if not is_private else HikariUndefined
            )

            await thread.send(initial_message)

            return str(thread.id)
        except HikariForbiddenError as error:
            raise ForbiddenError(
                f"Cannot create a new thread in the channel '{channel_id}' of server '{server_id}'."
            ) from error

    async def add_thread_member(
        self,
        thread_id: str,
        user_id: str
    ) -> None:
        assert_not_none(thread_id, "thread_id")
        assert_not_none(user_id, "user_id")

        try:
            await get_bot().rest.add_thread_member(
                int(thread_id),
                int(user_id)
            )
        except HikariForbiddenError as error:
            raise ForbiddenError(
                f"Cannot add user '{user_id}' to thread '{thread_id}'."
            ) from error
        except HikariNotFoundError as error:
            raise ThreadNotFoundError(thread_id) from error
