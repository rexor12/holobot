from collections.abc import Iterable
from random import randint

from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.utils import escape_user_text
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import (
    Cooldown, InteractionResponse, StringOption
)
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class ChooseItemWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider
    ) -> None:
        super().__init__()
        self.__i18n = i18n_provider

    @command(
        description="Randomly chooses one of the specified items.",
        group_name="random",
        name="choose",
        options=(
            StringOption("item1", "The first item.", OptionType.STRING, True, max_length=50),
            StringOption("item2", "The second item.", OptionType.STRING, True, max_length=50),
            StringOption("item3", "The third item.", OptionType.STRING, False, max_length=50),
            StringOption("item4", "The fourth item.", OptionType.STRING, False, max_length=50),
            StringOption("item5", "The fifth item.", OptionType.STRING, False, max_length=50),
            StringOption("item6", "The sixth item.", OptionType.STRING, False, max_length=50),
            StringOption("item7", "The seventh item.", OptionType.STRING, False, max_length=50),
            StringOption("item8", "The eighth item.", OptionType.STRING, False, max_length=50),
        ),
        cooldown=Cooldown(duration=5)
    )
    async def choose_item(
        self,
        context: InteractionContext,
        item1: str,
        item2: str,
        item3: str | None = None,
        item4: str | None = None,
        item5: str | None = None,
        item6: str | None = None,
        item7: str | None = None,
        item8: str | None = None
    ) -> InteractionResponse:
        chosen_item = ChooseItemWorkflow.__choice_reservoir(
            (item1, item2, item3, item4, item5, item6, item7, item8)
        )

        return self._reply(
            content=self.__i18n.get(
                "extensions.general.choose_item_workflow.result",
                {
                    "result": escape_user_text(chosen_item)
                }
            )
        )

    @staticmethod
    def __choice_reservoir(items: Iterable[str | None]) -> str:
        chosen_item: str | None = None
        count = 0
        for item in items:
            if item is None:
                continue

            count += 1
            if randint(1, count) == 1:
                chosen_item = item

        if chosen_item is None:
            raise ValueError("All of the specified items are None. At least one item must be non-None.")

        return chosen_item
