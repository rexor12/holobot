from discord.errors import Forbidden
from discord.guild import Guild
from discord.role import Role as DiscordRole
from discord.utils import get
from holobot.discord.bot import BotAccessor
from holobot.discord.sdk.exceptions import ForbiddenError, RoleAlreadyExistsError, ServerNotFoundError
from holobot.discord.sdk.models import Role
from holobot.discord.sdk.servers.managers import IRoleManager
from holobot.discord.transformers.role import remote_to_local
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none
from typing import Optional

@injectable(IRoleManager)
class RoleManager(IRoleManager):
    def get_role(self, server_id: str, role_name: str) -> Optional[Role]:
        assert_not_none(server_id, "server_id")
        assert_not_none(role_name, "role_name")

        guild = RoleManager.__get_guild(server_id)
        role: Optional[DiscordRole] = get(guild.roles, name=role_name)
        return remote_to_local(role) if role else None

    async def create_role(self, server_id: str, role_name: str, description: str) -> Role:
        assert_not_none(server_id, "server_id")
        assert_not_none(role_name, "role_name")

        guild = RoleManager.__get_guild(server_id)
        role: Optional[DiscordRole] = get(guild.roles, name=role_name)
        if role:
            raise RoleAlreadyExistsError(server_id, role_name)

        try:
            role = await guild.create_role(name=role_name, reason=description)
            return remote_to_local(role)
        except Forbidden:
            raise ForbiddenError("Cannot create role.")

    @staticmethod
    def __get_guild(server_id: str) -> Guild:
        guild: Optional[Guild] = BotAccessor.get_bot().get_guild(int(server_id))
        if not guild:
            raise ServerNotFoundError(server_id)

        return guild
