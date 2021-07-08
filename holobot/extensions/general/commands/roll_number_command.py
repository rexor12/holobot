from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.utils import find_emoji, reply
from holobot.sdk.ioc import ServiceCollectionInterface
from holobot.sdk.ioc.decorators import injectable
from random import randint

@injectable(CommandInterface)
class RollNumberCommand(CommandBase):
    def __init__(self, services: ServiceCollectionInterface) -> None:
        super().__init__(services, "roll")
        self.description = "Generates a random integer between the specified bounds."
        self.options = [
            create_option("max", "The upper bound.", SlashCommandOptionType.INTEGER, True),
            create_option("min", "The lower bound. By default, it's 1.", SlashCommandOptionType.INTEGER, False)
        ]

    async def execute(self, context: SlashContext, max: int, min: int = 1) -> None:
        if max < min:
            (min, max) = (max, min)
        await reply(context, f"You rolled {randint(min, max)}")
