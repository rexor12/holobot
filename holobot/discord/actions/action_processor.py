import contextlib

import hikari.api.special_endpoints as hikari_endpoints
from hikari import (
    UNDEFINED, CommandInteraction, ComponentInteraction, MessageFlag, NotFoundError,
    PartialInteraction, ResponseType
)

from holobot.discord.sdk.actions import ActionBase, DoNothingAction, EditMessageAction, ReplyAction
from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.models import Embed
from holobot.discord.sdk.workflows.interactables.components import (
    ComponentBase, Layout, StackLayout
)
from holobot.discord.transformers.embed import to_dto
from holobot.discord.workflows.transformers import IComponentTransformer
from holobot.sdk.exceptions import ArgumentError
from holobot.sdk.ioc.decorators import injectable
from .iaction_processor import IActionProcessor

@injectable(IActionProcessor)
class ActionProcessor(IActionProcessor):
    def __init__(self, component_transformer: IComponentTransformer) -> None:
        super().__init__()
        self.__component_transformer = component_transformer

    async def process(
        self,
        context: PartialInteraction,
        action: ActionBase,
        deferral: DeferType = DeferType.NONE,
        is_ephemeral: bool = False
    ) -> None:
        if isinstance(action, DoNothingAction):
            return

        if isinstance(action, ReplyAction):
            await self.__process_reply(context, action, deferral, is_ephemeral)
        elif isinstance(action, EditMessageAction):
            await self.__process_edit_reference_message(context, action, deferral, is_ephemeral)

    async def __process_reply(
        self,
        interaction: PartialInteraction,
        action: ReplyAction,
        deferral: DeferType,
        is_ephemeral: bool
    ) -> None:
        if not isinstance(interaction, (CommandInteraction, ComponentInteraction)):
            raise ArgumentError("Replying to a message is valid for command and component interactions only.")

        content = action.content if isinstance(action.content, str) else None
        embed = to_dto(action.content) if isinstance(action.content, Embed) else None
        components = self.__component_transformer.transform_to_root_component(action.components)
        with contextlib.suppress(NotFoundError):
            if deferral == DeferType.NONE:
                await interaction.create_initial_response(
                    ResponseType.MESSAGE_CREATE,
                    content=content,
                    embed=embed or UNDEFINED,
                    components=components,
                    flags=MessageFlag.EPHEMERAL if is_ephemeral else MessageFlag.NONE,
                    user_mentions=not action.suppress_user_mentions or UNDEFINED
                )
                return

            if deferral == DeferType.DEFER_MESSAGE_CREATION:
                await interaction.edit_initial_response(
                    content=content,
                    embed=embed,
                    components=components,
                    user_mentions=not action.suppress_user_mentions or UNDEFINED
                )
                return

            raise ArgumentError(f"Cannot reply to an interaction deferred as '{deferral}'.")

    async def __process_edit_reference_message(
        self,
        interaction: PartialInteraction,
        action: EditMessageAction,
        deferral: DeferType,
        is_ephemeral: bool
    ) -> None:
        if not isinstance(interaction, ComponentInteraction):
            raise ArgumentError("Editing a reference message is valid for component interactions only.")

        content = action.content if isinstance(action.content, str) else None
        embed = to_dto(action.content) if isinstance(action.content, Embed) else None
        components = self.__component_transformer.transform_to_root_component(action.components)
        with contextlib.suppress(NotFoundError):
            if deferral == DeferType.NONE:
                await interaction.create_initial_response(
                    ResponseType.MESSAGE_UPDATE,
                    content=content,
                    embed=embed or UNDEFINED,
                    components=components,
                    flags=MessageFlag.EPHEMERAL if is_ephemeral else MessageFlag.NONE,
                    user_mentions=not action.suppress_user_mentions or UNDEFINED
                )
                return

            if deferral == DeferType.DEFER_MESSAGE_UPDATE:
                await interaction.edit_initial_response(
                    content=content,
                    embed=embed,
                    components=components,
                    user_mentions=not action.suppress_user_mentions or UNDEFINED
                )
                return

            raise ArgumentError(f"Cannot edit an interaction deferred as '{deferral}'.")
