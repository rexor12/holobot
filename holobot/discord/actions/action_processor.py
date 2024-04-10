import contextlib
from collections.abc import Callable
from typing import TypeVar

import hikari
import hikari.impl.special_endpoints as hikari_speps

from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.actions import (
    ActionBase, AutocompleteAction, DeleteAction, DoNothingAction, EditMessageAction, ReplyAction,
    ShowModalAction
)
from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.transformers.embed import to_dto as embed_to_dto
from holobot.discord.workflows.transformers import IComponentTransformer
from holobot.sdk.exceptions import ArgumentError, InvalidOperationError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils.type_utils import UndefinedType
from .iaction_processor import IActionProcessor

T = TypeVar("T")
TResult = TypeVar("TResult")

@injectable(IActionProcessor)
class ActionProcessor(IActionProcessor):
    def __init__(
        self,
        component_transformer: IComponentTransformer,
        messaging: IMessaging
    ) -> None:
        super().__init__()
        self.__component_transformer = component_transformer
        self.__messaging = messaging

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
            case DeleteAction(): await self.__process_delete(context, deferral)
            case ShowModalAction(): await self.__process_show_modal(context, action)

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
        if not isinstance(interaction, (hikari.CommandInteraction, hikari.ComponentInteraction, hikari.ModalInteraction)):
            raise ArgumentError("interaction", "Replying is valid for command, component and modal interactions only.")

        components = self.__component_transformer.create_controls(action.components)
        with contextlib.suppress(hikari.NotFoundError):
            if deferral is DeferType.NONE:
                should_be_ephemeral = (
                    action.is_ephemeral
                    if isinstance(action.is_ephemeral, bool)
                    else is_ephemeral
                )
                await interaction.create_initial_response(
                    hikari.ResponseType.MESSAGE_CREATE,
                    content=ActionProcessor.__convert_to_dto(action.content, lambda i: str(i)),
                    embed=ActionProcessor.__convert_to_dto(action.embed, embed_to_dto),
                    components=components,
                    flags=(
                        hikari.MessageFlag.EPHEMERAL
                        if should_be_ephemeral
                        else hikari.MessageFlag.NONE
                    ),
                    user_mentions=not action.suppress_user_mentions or hikari.UNDEFINED,
                    attachments=ActionProcessor.__convert_to_dto(action.attachments, lambda i: i)
                )
                return

            if deferral is DeferType.DEFER_MESSAGE_CREATION:
                await interaction.edit_initial_response(
                    content=ActionProcessor.__convert_to_dto(action.content, lambda i: str(i)),
                    embed=ActionProcessor.__convert_to_dto(action.embed, embed_to_dto),
                    components=components,
                    user_mentions=not action.suppress_user_mentions or hikari.UNDEFINED,
                    attachments=ActionProcessor.__convert_to_dto(action.attachments, lambda i: i)
                )
                return

            raise ArgumentError("deferral", f"Cannot reply to an interaction deferred as '{deferral}'.")

    async def __process_edit_reference_message(
        self,
        interaction: hikari.PartialInteraction,
        action: EditMessageAction,
        deferral: DeferType,
        is_ephemeral: bool
    ) -> None:
        if not isinstance(interaction, (hikari.ComponentInteraction, hikari.ModalInteraction)):
            raise ArgumentError("interaction", "Editing a reference message is valid for component interactions only.")

        components = self.__component_transformer.create_controls(action.components)
        with contextlib.suppress(hikari.NotFoundError):
            if deferral is DeferType.NONE:
                await interaction.create_initial_response(
                    hikari.ResponseType.MESSAGE_UPDATE,
                    content=ActionProcessor.__convert_to_dto(action.content, lambda i: str(i)),
                    embed=ActionProcessor.__convert_to_dto(action.embed, embed_to_dto),
                    components=components,
                    flags=hikari.MessageFlag.EPHEMERAL if is_ephemeral else hikari.MessageFlag.NONE,
                    user_mentions=not action.suppress_user_mentions or hikari.UNDEFINED,
                    attachments=ActionProcessor.__convert_to_dto(action.attachments, lambda i: i)
                )
                return

            if deferral is DeferType.DEFER_MESSAGE_UPDATE:
                await interaction.edit_initial_response(
                    content=ActionProcessor.__convert_to_dto(action.content, lambda i: str(i)),
                    embed=ActionProcessor.__convert_to_dto(action.embed, embed_to_dto),
                    components=components,
                    user_mentions=not action.suppress_user_mentions or hikari.UNDEFINED,
                    attachments=ActionProcessor.__convert_to_dto(action.attachments, lambda i: i)
                )
                return

            raise ArgumentError("deferral", f"Cannot edit an interaction deferred as '{deferral}'.")

    async def __process_autocomplete(
        self,
        interaction: hikari.PartialInteraction,
        action: AutocompleteAction,
    ) -> None:
        if not isinstance(interaction, (hikari.AutocompleteInteraction)):
            raise ArgumentError("interaction", "Responding to an autocompletion is valid for autocomplete interactions only.")

        with contextlib.suppress(hikari.NotFoundError):
            await interaction.create_response(
                choices=[
                    hikari_speps.AutocompleteChoiceBuilder(
                        choice.name,
                        choice.value
                    ) for choice in action.choices
                ]
            )

    async def __process_delete(
        self,
        interaction: hikari.PartialInteraction,
        deferral: DeferType
    ) -> None:
        with contextlib.suppress(hikari.NotFoundError):
            if isinstance(interaction, hikari.CommandInteraction):
                if deferral is DeferType.NONE:
                    raise InvalidOperationError("Cannot delete a non-deferred command interaction response.")

                await interaction.delete_initial_response()
            elif isinstance(interaction, hikari.ComponentInteraction):
                if deferral is DeferType.NONE:
                    await self.__messaging.delete_message(
                        str(interaction.channel_id),
                        str(interaction.message.id)
                    )
                    return

                await interaction.delete_message(interaction.message.id)
            else:
                raise ArgumentError("interaction", "Replying to a message is valid for command and component interactions only.")

    async def __process_show_modal(
        self,
        interaction: hikari.PartialInteraction,
        action: ShowModalAction
    ) -> None:
        if not isinstance(interaction, (hikari.CommandInteraction, hikari.ComponentInteraction)):
            raise ArgumentError("interaction", "Showing a modal is valid for command and component interactions only.")

        with contextlib.suppress(hikari.NotFoundError):
            await interaction.create_modal_response(
                action.modal.title,
                action.modal.identifier,
                components=self.__component_transformer.create_modal(action.modal)
            )
            return
