import contextlib
from collections.abc import Callable
from typing import TypeVar

import hikari

from holobot.discord.sdk.actions import (
    ActionBase, AutocompleteAction, DeleteAction, DoNothingAction, EditMessageAction, ReplyAction
)
from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.transformers.embed import to_dto as embed_to_dto
from holobot.discord.workflows.transformers import IComponentTransformer
from holobot.sdk.exceptions import ArgumentError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils.type_utils import UndefinedType
from .iaction_processor import IActionProcessor

T = TypeVar("T")
TResult = TypeVar("TResult")

@injectable(IActionProcessor)
class ActionProcessor(IActionProcessor):
    def __init__(self, component_transformer: IComponentTransformer) -> None:
        super().__init__()
        self.__component_transformer = component_transformer

    async def process(
        self,
        context: hikari.PartialInteraction,
        action: ActionBase,
        deferral: DeferType = DeferType.NONE,
        is_ephemeral: bool = False
    ) -> None:
        match action:
            case DoNothingAction(): return
            case ReplyAction(): await self.__process_reply(context, action, deferral, is_ephemeral)
            case EditMessageAction(): await self.__process_edit_reference_message(context, action, deferral, is_ephemeral)
            case AutocompleteAction(): await self.__process_autocomplete(context, action)
            case DeleteAction(): await self.__process_delete(context)

    @staticmethod
    def __convert_to_dto(
        value: T | None | UndefinedType,
        converter: Callable[[T], TResult]
    ) -> TResult | None | hikari.UndefinedType:
        match value:
            case UndefinedType():
                return hikari.UNDEFINED
            case None:
                return None
            case _:
                return converter(value)

    async def __process_reply(
        self,
        interaction: hikari.PartialInteraction,
        action: ReplyAction,
        deferral: DeferType,
        is_ephemeral: bool
    ) -> None:
        if not isinstance(interaction, (hikari.CommandInteraction, hikari.ComponentInteraction)):
            raise ArgumentError("Replying to a message is valid for command and component interactions only.")

        components = self.__component_transformer.transform_to_root_component(action.components)
        with contextlib.suppress(hikari.NotFoundError):
            if deferral is DeferType.NONE:
                await interaction.create_initial_response(
                    hikari.ResponseType.MESSAGE_CREATE,
                    content=ActionProcessor.__convert_to_dto(action.content, lambda i: str(i)),
                    embed=ActionProcessor.__convert_to_dto(action.embed, embed_to_dto),
                    components=components,
                    flags=hikari.MessageFlag.EPHEMERAL if is_ephemeral else hikari.MessageFlag.NONE,
                    user_mentions=not action.suppress_user_mentions or hikari.UNDEFINED
                )
                return

            if deferral is DeferType.DEFER_MESSAGE_CREATION:
                await interaction.edit_initial_response(
                    content=ActionProcessor.__convert_to_dto(action.content, lambda i: str(i)),
                    embed=ActionProcessor.__convert_to_dto(action.embed, embed_to_dto),
                    components=components,
                    user_mentions=not action.suppress_user_mentions or hikari.UNDEFINED
                )
                return

            raise ArgumentError(f"Cannot reply to an interaction deferred as '{deferral}'.")

    async def __process_edit_reference_message(
        self,
        interaction: hikari.PartialInteraction,
        action: EditMessageAction,
        deferral: DeferType,
        is_ephemeral: bool
    ) -> None:
        if not isinstance(interaction, hikari.ComponentInteraction):
            raise ArgumentError("Editing a reference message is valid for component interactions only.")

        components = self.__component_transformer.transform_to_root_component(action.components)
        with contextlib.suppress(hikari.NotFoundError):
            if deferral is DeferType.NONE:
                await interaction.create_initial_response(
                    hikari.ResponseType.MESSAGE_UPDATE,
                    content=ActionProcessor.__convert_to_dto(action.content, lambda i: str(i)),
                    embed=ActionProcessor.__convert_to_dto(action.embed, embed_to_dto),
                    components=components,
                    flags=hikari.MessageFlag.EPHEMERAL if is_ephemeral else hikari.MessageFlag.NONE,
                    user_mentions=not action.suppress_user_mentions or hikari.UNDEFINED
                )
                return

            if deferral is DeferType.DEFER_MESSAGE_UPDATE:
                await interaction.edit_initial_response(
                    content=ActionProcessor.__convert_to_dto(action.content, lambda i: str(i)),
                    embed=ActionProcessor.__convert_to_dto(action.embed, embed_to_dto),
                    components=components,
                    user_mentions=not action.suppress_user_mentions or hikari.UNDEFINED
                )
                return

            raise ArgumentError(f"Cannot edit an interaction deferred as '{deferral}'.")

    async def __process_autocomplete(
        self,
        interaction: hikari.PartialInteraction,
        action: AutocompleteAction,
    ) -> None:
        if not isinstance(interaction, (hikari.AutocompleteInteraction)):
            raise ArgumentError("Responding to an autocompletion is valid for autocomplete interactions only.")

        with contextlib.suppress(hikari.NotFoundError):
            await interaction.create_response(
                choices=[
                    hikari.CommandChoice(
                        name=choice.name,
                        value=choice.value
                    )
                    for choice in action.choices
                ]
            )

    async def __process_delete(
        self,
        interaction: hikari.PartialInteraction
    ) -> None:
        if not isinstance(interaction, (hikari.CommandInteraction, hikari.ComponentInteraction)):
            raise ArgumentError("Replying to a message is valid for command and component interactions only.")

        with contextlib.suppress(hikari.NotFoundError):
            await interaction.delete_initial_response()
