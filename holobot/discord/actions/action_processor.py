from holobot.sdk.exceptions.argument_error import ArgumentError
from .iaction_processor import IActionProcessor
from ..components.icomponent_transformer import IComponentTransformer
from discord_slash.context import ComponentContext, MenuContext, SlashContext
from holobot.discord.sdk.actions import ActionBase, DoNothingAction, ReplyAction
from holobot.discord.sdk.components import Component, StackLayout
from holobot.discord.sdk.models import Embed
from holobot.discord.transformers.embed import local_to_remote
from holobot.sdk.ioc.decorators import injectable
from typing import Any, Dict, List, Union

@injectable(IActionProcessor)
class ActionProcessor(IActionProcessor):
    def __init__(self, component_transformer: IComponentTransformer) -> None:
        super().__init__()
        self.__component_transformer: IComponentTransformer = component_transformer
    
    async def process(self, context: Union[ComponentContext, MenuContext, SlashContext], action: ActionBase) -> None:
        if isinstance(action, DoNothingAction):
            return

        if isinstance(action, ReplyAction):
            components = self.__transform_component(action.components)
            if isinstance(action.content, Embed):
                await context.send(embed=local_to_remote(action.content), components=components)
            else: await context.send(action.content, components=components)

    def __transform_component(self, components: Union[Component, List[StackLayout]]) -> List[Dict[str, Any]]:
        if not components:
            return []

        if isinstance(components, list):
            if len(components) == 0:
                return []
        else: components = [StackLayout(id="auto_wrapper_stack_layout", children=[components])]
        
        if len(components) > 5:
            raise ArgumentError("components", "A message cannot hold more than 5 layouts.")

        return [
            self.__component_transformer.transform_component(component)
            for component in components
        ]
