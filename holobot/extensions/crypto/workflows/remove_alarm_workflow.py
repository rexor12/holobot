from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable
from .. import AlertManagerInterface
from ..utils import is_valid_symbol

@injectable(IWorkflow)
class RemoveAlarmWorkflow(WorkflowBase):
    def __init__(self, alert_manager: AlertManagerInterface) -> None:
        super().__init__()
        self.__alert_manager: AlertManagerInterface = alert_manager

    @command(
        description="Removes all of your alarms associated to a symbol.",
        name="remove",
        group_name="crypto",
        subgroup_name="alarm",
        options=(
            Option("symbol", "The symbol, such as BTCEUR."),
        )
    )
    async def remove_alarm(
        self,
        context: ServerChatInteractionContext,
        symbol: str
    ) -> InteractionResponse:
        symbol = symbol.upper()
        if not is_valid_symbol(symbol):
            return InteractionResponse(
                action=ReplyAction(content="The symbol you specified isn't in the accepted format.")
            )
        alerts = await self.__alert_manager.remove_many(context.author_id, symbol)
        return InteractionResponse(
            action=ReplyAction(content=f"All {len(alerts)} of your alerts set for {symbol} have been removed.")
        )
