from discord_slash.context import ComponentContext
from holobot.discord.sdk.components.models import ComponentRegistration

class IComponentInteractionProcessor:
    async def process(self, registration: ComponentRegistration, context: ComponentContext) -> None:
        raise NotImplementedError
