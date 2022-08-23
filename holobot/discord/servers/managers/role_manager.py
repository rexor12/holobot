from hikari import ForbiddenError as HikariForbiddenError, Guild

from holobot.discord.bot import get_bot
from holobot.discord.sdk.exceptions import (
    ForbiddenError, RoleAlreadyExistsError, ServerNotFoundError
)
from holobot.discord.sdk.models import Role
from holobot.discord.sdk.servers.managers import IRoleManager
from holobot.discord.transformers.role import to_model
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none, first_or_default

@injectable(IRoleManager)
class RoleManager(IRoleManager):
    def get_role(self, server_id: str, role_name: str) -> Role | None:
        assert_not_none(server_id, "server_id")
        assert_not_none(role_name, "role_name")

        guild = RoleManager.__get_guild(server_id)
        role = first_or_default(guild.get_roles().values(), lambda r: r.name == role_name)
        return to_model(role) if role else None

    async def create_role(self, server_id: str, role_name: str, description: str) -> Role:
        assert_not_none(server_id, "server_id")
        assert_not_none(role_name, "role_name")

        guild = RoleManager.__get_guild(server_id)
        if role := first_or_default(guild.get_roles().values(), lambda r: r.name == role_name):
            raise RoleAlreadyExistsError(server_id, role_name)

        try:
            role = await get_bot().rest.create_role(
                guild,
                name=role_name,
                reason=description
            )
            return to_model(role)
        except HikariForbiddenError as error:
            raise ForbiddenError("Cannot create role.") from error

    @staticmethod
    def __get_guild(server_id: str) -> Guild:
        guild = get_bot().cache.get_guild(int(server_id))
        if not guild:
            raise ServerNotFoundError(server_id)
        return guild
