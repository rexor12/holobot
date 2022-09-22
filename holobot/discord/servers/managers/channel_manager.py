from collections.abc import Iterable

from hikari import (
    BadRequestError as HikariBadRequestError, ChannelFollowerWebhook,
    ForbiddenError as HikariForbiddenError, GuildNewsChannel, PermissionOverwrite,
    PermissionOverwriteType, Permissions, Snowflake
)

from holobot.discord.bot import get_bot
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.exceptions import (
    ChannelNotFoundError, ForbiddenError, InvalidChannelError, PermissionError, RoleNotFoundError
)
from holobot.discord.sdk.servers.managers import IChannelManager
from holobot.discord.sdk.servers.models import ServerChannel
from holobot.discord.transformers.server_channel import to_model
from holobot.discord.utils import get_guild
from holobot.discord.utils.permission_utils import PERMISSION_TO_DTOS
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none

@injectable(IChannelManager)
class ChannelManager(IChannelManager):
    def get_channels(self, server_id: str) -> Iterable[ServerChannel]:
        assert_not_none(server_id, "server_id")
        return list(map(to_model, get_guild(server_id).get_channels().values()))

    async def set_role_permissions(
        self,
        server_id: str,
        channel_id: str,
        role_id: str,
        *permissions: tuple[Permission, bool | None]
    ) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(channel_id, "channel_id")
        assert_not_none(role_id, "role_id")

        if not permissions:
            return

        guild = get_guild(server_id)
        if not (channel := guild.get_channel(int(channel_id))):
            raise ChannelNotFoundError(channel_id)

        if not guild.get_role(int(role_id)):
            raise RoleNotFoundError(server_id, role_id)

        allowed_permissions = Permissions.NONE
        denied_permissions = Permissions.NONE
        for permission, status in permissions:
            if (permission_dto := PERMISSION_TO_DTOS.get(permission)) is None:
                # This may also be a programming error if the map doesn't contain a newly introduced flag.
                raise PermissionError(permission, "There is no matching Discord permission. Make sure a single flag is specified only.")
            if status is True:
                allowed_permissions |= permission_dto
            elif status is False:
                denied_permissions |= permission_dto

        new_permission_overwrites = [*channel.permission_overwrites.values()]
        new_permission_overwrites.append(
            PermissionOverwrite(
                id=Snowflake(role_id),
                type=PermissionOverwriteType.ROLE,
                allow=allowed_permissions,
                deny=denied_permissions
            )
        )
        try:
            await channel.edit(permission_overwrites=new_permission_overwrites)
        except HikariForbiddenError as error:
            raise ForbiddenError(f"Cannot set permissions for role '{role_id}' and channel '{channel_id}'.") from error

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

        guild = get_guild(server_id)
        if not (channel := guild.get_channel(int(channel_id))):
            raise ChannelNotFoundError(channel_id)

        source_guild = get_guild(source_server_id)
        if not (source_channel := source_guild.get_channel(int(source_channel_id))):
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
            raise ForbiddenError("Cannot follow news channel.") from error
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

        guild = get_guild(server_id)
        try:
            webhooks = await get_bot().rest.fetch_guild_webhooks(guild)
            for webhook in webhooks:
                if (
                    isinstance(webhook, ChannelFollowerWebhook)
                    and str(webhook.source_guild.id) == source_server_id
                    and str(webhook.source_channel.id) == source_channel_id
                ):
                    await get_bot().rest.delete_webhook(webhook)
        except HikariForbiddenError as error:
            raise ForbiddenError("Cannot unfollow news channel.") from error
