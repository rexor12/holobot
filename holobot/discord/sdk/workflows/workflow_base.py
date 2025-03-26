from collections.abc import Sequence

from holobot.discord.sdk.actions import (
    AutocompleteAction, DeleteAction, EditMessageAction, ReplyAction, ShowModalAction
)
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.models import AutocompleteChoice, Embed
from holobot.discord.sdk.workflows.interactables.components import ComponentBase, LayoutBase
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.discord.sdk.workflows.interactables.views import Modal
from holobot.sdk.utils.type_utils import UNDEFINED, UndefinedOrNoneOr, UndefinedType
from .constants import DECORATOR_METADATA_NAME, WORKFLOW_PREDEFINED_INTERACTABLES
from .interactables import Interactable
from .iworkflow import IWorkflow

class WorkflowBase(IWorkflow):
    @property
    def name(self) -> str:
        return self.__name

    @property
    def required_permissions(self) -> Permission:
        return self.__required_permissions

    @property
    def interactables(self) -> tuple[Interactable, ...]:
        return tuple(self.__interactables)

    # This method is responsible for collecting the interactables
    # that decorators have set up in the class or its base classes.
    def __init_subclass__(cls) -> None:
        interactables = list[Interactable]()

        # Collect any interactables base classes may have already added.
        for base in cls.__bases__:
            interactables.extend(getattr(base, WORKFLOW_PREDEFINED_INTERACTABLES, ()))

        # Add the current class's own interactables defined by decorators.
        for member in cls.__dict__.values():
            if workflow_metadata := getattr(member, DECORATOR_METADATA_NAME, None):
                interactables.append(workflow_metadata)

        setattr(cls, WORKFLOW_PREDEFINED_INTERACTABLES, interactables)

    def __init__(
        self,
        *,
        name: str | None = None,
        interactables: tuple[Interactable, ...] = (),
        required_permissions: Permission = Permission.NONE
    ) -> None:
        self.__name: str = name or type(self).__name__
        self.__required_permissions: Permission = required_permissions
        predefined_interactables: list[Interactable] = getattr(
            self,
            WORKFLOW_PREDEFINED_INTERACTABLES,
            []
        )
        self.__interactables: list[Interactable] = list(predefined_interactables)
        self.__interactables.extend(interactables)

    def __str__(self) -> str:
        return type(self).__name__

    def add_registration(self, registration: Interactable) -> None:
        self.__interactables.append(registration)

    def _reply(
        self,
        *,
        content: str | None = None,
        embed: Embed | None = None,
        components: ComponentBase | list[LayoutBase] | None = None,
        suppress_user_mentions: bool = False,
        is_ephemeral: bool | UndefinedType = UNDEFINED,
        attachments: Sequence[bytes] | UndefinedType = UNDEFINED
    ) -> InteractionResponse:
        """Reply to the interaction with a normal message.

        :param content: The text content of the message, defaults to None
        :type content: str | None, optional
        :param embed: The embed content of the message, defaults to None
        :type embed: Embed | None, optional
        :param components: Zero or more components to attach to the message, defaults to None
        :type components: ComponentBase | list[LayoutBase] | None, optional
        :param suppress_user_mentions: Whether user mentions should be suppressed to avoid pings, defaults to False
        :type suppress_user_mentions: bool, optional
        :param is_ephemeral: Whether the response is ephemeral. This parameter overrides the associated interactable's preference if and only if the response is not deferred.
        :type is_ephemeral: bool | UndefinedType, optional
        :param attachments: Files to be attached to the message.
        :type attachments: Sequence[bytes] | UndefinedType, optional
        :return: The interaction response.
        :rtype: InteractionResponse
        """

        return InteractionResponse(
            action=ReplyAction(
                content=content,
                embed=embed,
                components=components or [],
                suppress_user_mentions=suppress_user_mentions,
                is_ephemeral=is_ephemeral,
                attachments=attachments
            )
        )

    def _edit_message(
        self,
        *,
        content: UndefinedOrNoneOr[str] = UNDEFINED,
        embed: UndefinedOrNoneOr[Embed] = UNDEFINED,
        components: ComponentBase | list[LayoutBase] | None = None,
        suppress_user_mentions: bool = False,
        attachments: Sequence[bytes] | None | UndefinedType = UNDEFINED
    ) -> InteractionResponse:
        """Edit an already existing message while keeping any undefined components.

        This is typically useful for component interactions.

        :param content: The text content of the message, defaults to UNDEFINED
        :type content: UndefinedOrNoneOr[str], optional
        :param embed: The embed content of the message, defaults to UNDEFINED
        :type embed: UndefinedOrNoneOr[Embed], optional
        :param components: Zero or more components to attach to the message, defaults to None
        :type components: ComponentBase | list[LayoutBase] | None, optional
        :param suppress_user_mentions: Whether user mentions should be suppressed to avoid pings, defaults to False
        :type suppress_user_mentions: bool, optional
        :param attachments: Files to be attached to the message.
        :type attachments: Sequence[bytes] | None | UndefinedType, optional
        :return: The interaction response.
        :rtype: InteractionResponse
        """

        return InteractionResponse(
            action=EditMessageAction(
                content=content,
                embed=embed,
                components=components or [],
                suppress_user_mentions=suppress_user_mentions,
                attachments=attachments
            )
        )

    def _clear_message(
        self,
        *,
        content: str | None = None,
        embed: Embed | None = None,
        components: ComponentBase | list[LayoutBase] | None = None,
        suppress_user_mentions: bool = False,
        attachments: Sequence[bytes] | None = None
    ) -> InteractionResponse:
        """Edit an already existing message while clearing the unspecified components.

        This is typically useful for component interactions.

        :param content: The text content of the message, defaults to None
        :type content: str | None, optional
        :param embed: The embed content of the message, defaults to None
        :type embed: Embed | None, optional
        :param components: Zero or more components to attach to the message, defaults to None
        :type components: ComponentBase | list[LayoutBase] | None, optional
        :param suppress_user_mentions: Whether user mentions should be suppressed to avoid pings, defaults to False
        :type suppress_user_mentions: bool, optional
        :param attachments: Files to be attached to the message.
        :type attachments: Sequence[bytes] | None, optional
        :return: The interaction response.
        :rtype: InteractionResponse
        """

        return InteractionResponse(
            action=EditMessageAction(
                content=content,
                embed=embed,
                components=components or [],
                suppress_user_mentions=suppress_user_mentions,
                attachments=attachments
            )
        )

    def _autocomplete(
        self,
        choices: AutocompleteChoice | list[AutocompleteChoice]
    ) -> InteractionResponse:
        """Return the auto-complete values.

        :param choices: The only available choice or a list of them.
        :type choices: AutocompleteChoice | list[AutocompleteChoice]
        :return: The interaction response.
        :rtype: InteractionResponse
        """

        return InteractionResponse(
            action=AutocompleteAction(
                choices=choices if isinstance(choices, list) else [choices]
            )
        )

    def _delete(self) -> InteractionResponse:
        """Delete the initial interaction response.

        This is useful when you don't want the reply-like information
        to appear above the response so as to hide the command usage.

        The response must be deferred in order for this to work;
        otherwise, an interaction failure is reported to the user.

        :return: The interaction response.
        :rtype: InteractionResponse
        """

        return InteractionResponse(
            action=DeleteAction()
        )

    def _show_modal(
        self,
        modal: Modal
    ) -> InteractionResponse:
        """Displays a modal to the invoking user.

        :param modal: The modal to be displayed.
        :type modal: Modal
        :return: The interaction response.
        :rtype: InteractionResponse
        """

        return InteractionResponse(
            action=ShowModalAction(
                modal=modal
            )
        )
