from random import randint

from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class RollNumberWorkflow(WorkflowBase):
    def __init__(self) -> None:
        super().__init__()

    @command(
        description="Generates a random integer between the specified bounds.",
        name="roll",
        options=(
            Option("max", "The upper bound.", OptionType.INTEGER, True),
            Option("min", "The lower bound. By default, it's 1.", OptionType.INTEGER, False)
        )
    )
    async def roll_number(
        self,
        context: ServerChatInteractionContext,
        max: int,
        min: int = 1
    ) -> InteractionResponse:
        if max < min:
            (min, max) = (max, min)

        return InteractionResponse(
            action=ReplyAction(content=f"You rolled {randint(min, max)}.")
        )
