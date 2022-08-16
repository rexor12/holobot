from holobot.discord.sdk.models import Role

class IRoleManager:
    def get_role(self, server_id: str, role_name: str) -> Role | None:
        raise NotImplementedError

    async def create_role(self, server_id: str, role_name: str, description: str) -> Role:
        raise NotImplementedError
