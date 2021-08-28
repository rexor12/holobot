from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, Option, ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable
from random import Random
from typing import Tuple

@injectable(CommandInterface)
class MagicEightBallCommand(CommandBase):
    def __init__(self) -> None:
        super().__init__("8ball")
        self.description = "Answers your yes/no question."
        self.options = [
            Option("question", "The yes/no question to be answered.")
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

    async def execute(self, context: ServerChatInteractionContext, question: str) -> CommandResponse:
        seed = question.strip().strip("?.!-+").lower().__hash__()
        return CommandResponse(
            action=ReplyAction(content=Random(seed).choice(self.__answers))
        )
