from random import randint

from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse, Option
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

_NAMED_DICE = {1, 4, 6, 8, 10, 12, 20, 24, 50, 120}

@injectable(IWorkflow)
class RollNumberWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider

    @command(
        description="Generates a random integer between the specified bounds.",
        name="roll",
        options=(
            Option("max", "The upper bound.", OptionType.INTEGER, True),
            Option("min", "The lower bound. By default, it's 1.", OptionType.INTEGER, False)
        ),
        cooldown=Cooldown(duration=5)
    )
    async def roll_number(
        self,
        context: InteractionContext,
        max: int,
        min: int = 1
    ) -> InteractionResponse:
        if max < min:
            (min, max) = (max, min)

        result = randint(min, max)
        die_name = ""
        message_key = "extensions.general.roll_number_workflow.unusual_roll_result"
        if min == 1 and max in _NAMED_DICE:
            die_name = self.__i18n_provider.get(
                f"extensions.general.roll_number_workflow.die_{max}"
            )
            message_key = "extensions.general.roll_number_workflow.usual_roll_result"

        return InteractionResponse(
            action=ReplyAction(content=self.__i18n_provider.get(
                message_key,
                {
                    "name": die_name,
                    "value": result
                }
            ))
        )
