from random import Random
from typing import Tuple

from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class MagicEightBallWorkflow(WorkflowBase):
    def __init__(self) -> None:
        super().__init__()
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

    @command(
        description="Answers your yes/no question.",
        name="8ball",
        options=(
            Option("question", "The yes/no question to be answered."),
        )
    )
    async def answer_question(
        self,
        context: ServerChatInteractionContext,
        question: str
    ) -> InteractionResponse:
        seed = question.strip().strip("?.!-+").lower().__hash__()
        return InteractionResponse(
            action=ReplyAction(content=Random(seed).choice(self.__answers))
        )
