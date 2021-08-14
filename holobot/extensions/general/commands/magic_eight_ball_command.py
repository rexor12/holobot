from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from holobot.discord.sdk.commands import CommandBase, CommandInterface, CommandResponse
from holobot.discord.sdk.utils import reply
from holobot.sdk.ioc.decorators import injectable
from random import Random
from typing import Tuple

@injectable(CommandInterface)
class MagicEightBallCommand(CommandBase):
    def __init__(self) -> None:
        super().__init__("8ball")
        self.description = "Answers your yes/no question."
        self.options = [
            create_option("question", "The yes/no question to be answered.", SlashCommandOptionType.STRING, True)
        ]
        self.__answers: Tuple[str, ...] = (
            # Positive answers.
            "Yes.",
            "But of course!",
            "Certainly.",
            "Without a doubt.",
            "Yes, definitely.",
            "Most likely.",
            "It seems to be the case.",

            # Negative answers.
            "No.",
            "Of course, not!",
            "Quite unlikely.",
            "Don't count on it.",
            "I don't think so.",

            # Neutral answers.
            "Maybe.",
            "You don't have to know that.",
            "That's not your cup of tea.",
            "Who knows..."
        )

    async def execute(self, context: SlashContext, question: str) -> CommandResponse:
        seed = question.strip().strip("?.!-+").lower().__hash__()
        await reply(context, Random(seed).choice(self.__answers))
        return CommandResponse()
