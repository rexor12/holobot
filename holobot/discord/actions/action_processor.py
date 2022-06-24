from .iaction_processor import IActionProcessor
from ..components.icomponent_transformer import IComponentTransformer
from hikari import CommandInteraction, ComponentInteraction, PartialInteraction
from holobot.discord.sdk.actions import ActionBase, DoNothingAction, ReplyAction
from holobot.discord.sdk.components import Component, StackLayout
from holobot.discord.sdk.models import Embed
from holobot.discord.transformers.embed import to_dto
from holobot.sdk.exceptions import ArgumentError
from holobot.sdk.ioc.decorators import injectable
from typing import List, Union

import hikari.api.special_endpoints as hikari_endpoints

@injectable(IActionProcessor)
class ActionProcessor(IActionProcessor):
    def __init__(self, component_transformer: IComponentTransformer) -> None:
        super().__init__()
        self.__component_transformer: IComponentTransformer = component_transformer

    async def process(self, context: PartialInteraction, action: ActionBase) -> None:
        if isinstance(action, DoNothingAction):
            return

        if isinstance(action, ReplyAction):
            await self.__process_reply(context, action)

    async def __process_reply(self, interaction: PartialInteraction, action: ReplyAction) -> None:
        if not isinstance(interaction, (CommandInteraction, ComponentInteraction)):
            return

        await interaction.edit_initial_response(
            content=action.content if isinstance(action.content, str) else None,
            embed=to_dto(action.content) if isinstance(action.content, Embed) else None,
            components=self.__transform_component(action.components)
        )

    def __transform_component(
        self,
        components: Union[Component, List[StackLayout]]
    ) -> List[hikari_endpoints.ComponentBuilder]:
        if not components:
            return []

        if isinstance(components, list):
            if len(components) == 0:
                return []
        elif not isinstance(components, StackLayout):
            components = [StackLayout(id="auto_wrapper_stack_layout", children=[components])]
        else: components = [components]

        if len(components) > 5:
            raise ArgumentError("components", "A message cannot hold more than 5 layouts.")

        return [
            self.__component_transformer.transform_component(component)
            for component in components
        ]
