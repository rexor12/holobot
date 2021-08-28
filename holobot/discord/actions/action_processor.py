from .iaction_processor import IActionProcessor
from discord_slash.context import MenuContext, SlashContext
from holobot.discord.sdk.actions import ActionBase, DoNothingAction, ReplyAction
from holobot.discord.sdk.models import Embed
from holobot.discord.transformers.embed import local_to_remote
from holobot.sdk.ioc.decorators import injectable
from typing import Union

@injectable(IActionProcessor)
class ActionProcessor(IActionProcessor):
    async def process(self, context: Union[MenuContext, SlashContext], action: ActionBase) -> None:
        if isinstance(action, DoNothingAction):
            return

        if isinstance(action, ReplyAction):
            if isinstance(action.content, Embed):
                await context.send(embed=local_to_remote(action.content))
            else: await context.send(action.content)
            return
