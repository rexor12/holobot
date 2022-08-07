from hikari import ForbiddenError as HikariForbiddenError, PermissionOverwrite, PermissionOverwriteType, Permissions, Snowflake
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.exceptions import ChannelNotFoundError, ForbiddenError, PermissionError, RoleNotFoundError
from holobot.discord.sdk.servers.managers import IChannelManager
from holobot.discord.sdk.servers.models import ServerChannel
from holobot.discord.transformers.server_channel import to_model
from holobot.discord.utils import get_guild
from holobot.discord.utils.permission_utils import PERMISSION_TO_DTOS
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none
from typing import Iterable, Tuple, Union

@injectable(IChannelManager)
class ChannelManager(IChannelManager):
    def get_channels(self, server_id: str) -> Iterable[ServerChannel]:
        assert_not_none(server_id, "server_id")

        guild = get_guild(server_id)
        return [to_model(channel) for channel in guild.get_channels().values()]

    async def set_role_permissions(self, server_id: str, channel_id: str, role_id: str, *permissions: Tuple[Permission, Union[bool, None]]) -> None:
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
            if (permission_dto := PERMISSION_TO_DTOS.get(permission, None)) is None:
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
