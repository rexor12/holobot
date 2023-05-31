import time
from random import Random

from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse, Option
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.lifecycle import IStartable

@injectable(IStartable)
@injectable(IWorkflow)
class MagicEightBallWorkflow(WorkflowBase, IStartable):
    def __init__(
        self,
        i18n_provider: II18nProvider
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__answers: tuple[str, ...] =  ()

    async def start(self):
        self.__answers = self.__i18n_provider.get_list(
            "extensions.general.magic_eight_ball_workflow.responses"
        )

    async def stop(self):
        pass

    @command(
        description="Answers your yes/no question.",
        name="8ball",
        options=(
            Option("question", "The yes/no question to be answered."),
        ),
        cooldown=Cooldown(
            duration=10,
            message="extensions.general.magic_eight_ball_workflow.cooldown_error"
        )
    )
    async def answer_question(
        self,
        context: InteractionContext,
        question: str
    ) -> InteractionResponse:
        question = question.strip()
        seed = hash(question.strip("?.!-+").lower()) + int(time.time() / 60)

        return self._reply(
            content=self.__i18n_provider.get(
                "extensions.general.magic_eight_ball_workflow.response_message",
                {
                    "user_id": context.author_id,
                    "question": question,
                    "answer": Random(seed).choice(self.__answers)
                }
            ),
            suppress_user_mentions=True
        )
