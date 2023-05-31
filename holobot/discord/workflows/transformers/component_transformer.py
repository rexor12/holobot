from collections.abc import Callable, Iterable
from itertools import islice
from typing import Any, NamedTuple, cast

import hikari
import hikari.api.special_endpoints as endpointsintf
import hikari.impl.special_endpoints as endpoints

from holobot.discord import DiscordOptions
from holobot.discord.sdk.utils.string_utils import escape_user_input
from holobot.discord.sdk.workflows.interactables.components import (
    Button, ButtonState, ComboBox, ComboBoxState, ComponentBase, ComponentStateBase, ComponentStyle,
    EmptyState, LayoutBase, PagerState, Paginator, StackLayout, TextBox, TextBoxState, TextBoxStyle
)
from holobot.discord.sdk.workflows.interactables.views import Modal, ModalState
from holobot.sdk.configs import IOptions
from holobot.sdk.exceptions import ArgumentError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none, assert_range, try_parse_int
from .icomponent_transformer import IComponentTransformer

PRIMARY_COMPONENT_STYLE_ID: int = 1

COMPONENT_STYLE_MAP: dict[ComponentStyle, hikari.InteractiveButtonTypesT] = {
    ComponentStyle.PRIMARY: hikari.ButtonStyle.PRIMARY,
    ComponentStyle.SECONDARY: hikari.ButtonStyle.SECONDARY,
    ComponentStyle.SUCCESS: hikari.ButtonStyle.SUCCESS,
    ComponentStyle.DANGER: hikari.ButtonStyle.DANGER
}

_TComponentBuilder = Callable[
    [Any, endpointsintf.ComponentBuilder | None],
    endpointsintf.ComponentBuilder
]

class _ComponentData(NamedTuple):
    identifier: str
    data: str

@injectable(IComponentTransformer)
class ComponentTransformer(IComponentTransformer):
    def __init__(
        self,
        options: IOptions[DiscordOptions]
    ) -> None:
        super().__init__()
        self.__options = options
        self.__component_transformers: dict[type[ComponentBase], _TComponentBuilder] = {
            StackLayout: self.__transform_stack_layout,
            Paginator: self.__transform_pager,
            Button: self.__transform_button,
            ComboBox: self.__transform_combo_box,
            TextBox: self.__transform_text_box
        }
        self.__state_transformers: dict[type[ComponentBase], Callable[[hikari.ComponentInteraction], ComponentStateBase]] = {
            StackLayout: lambda i: EmptyState(identifier=i.custom_id, owner_id=str(i.user.id)),
            Paginator: self.__transform_pager_state,
            Button: self.__transform_button_state,
            ComboBox: self.__transform_combo_box_state
        }

    def transform_control(self, components: ComponentBase | list[LayoutBase]) -> list[endpointsintf.ComponentBuilder]:
        match components:
            case LayoutBase():
                components = [components]
            case ComponentBase():
                components = [StackLayout(id="auto_wrapper_stack_layout", children=[components])]
            case list() if len(components) > 5:
                raise ArgumentError("components", "A message cannot hold more than 5 layouts.")
        return list(map(lambda c: self.__transform_component(c, None), components))

    def transform_control_state(
        self,
        component_type: type[ComponentBase],
        interaction: hikari.ComponentInteraction
    ) -> ComponentStateBase:
        assert_not_none(component_type, "component_type")
        assert_not_none(interaction, "interaction")

        if not (transformer := self.__state_transformers.get(component_type)):
            raise ArgumentError("component_type", "Invalid component type.")
        return transformer(interaction)

    def transform_modal(
        self,
        view: Modal
    ) -> list[endpointsintf.ModalActionRowBuilder]:
        assert_range(len(view.title), 1, 45, "view.title")
        assert_range(len(view.components), 1, 5, "view.children")

        builders = []
        for child in view.components:
            if not isinstance(child, TextBox):
                raise ArgumentError("view.components", f"A modal cannot have a '{type(child)}' as its child.")

            builder = endpoints.ModalActionRowBuilder()
            self.__transform_component(child, builder)
            builders.append(builder)

        return builders

    def transform_modal_state(
        self,
        interaction: hikari.ModalInteraction
    ) -> ModalState:
        return ModalState(
            owner_id=str(interaction.user.id),
            components={
                state.identifier: state
                for state in self.__transform_modal_component_state(interaction, interaction.components)
            }
        )

    @staticmethod
    def __get_component_data_from_custom_id(custom_id: str) -> _ComponentData:
        custom_id_parts = custom_id.split("~", 1)
        return _ComponentData(
            custom_id_parts[0],
            custom_id_parts[1] if len(custom_id_parts) > 1 else ""
        )

    def __transform_component(
        self,
        component: ComponentBase,
        container: endpointsintf.ComponentBuilder | None
    ) -> endpointsintf.ComponentBuilder:
        assert_not_none(component, "component")
        assert_range(len(component.id), 1, 100, "component.id")

        if not (transformer := self.__component_transformers.get(type(component))):
            raise ArgumentError("component", "Invalid component type.")

        return transformer(component, container)

    def __transform_modal_component_state(
        self,
        interaction: hikari.ModalInteraction,
        component: hikari.ModalActionRowComponent
                   | hikari.ModalComponentTypesT
                   | Iterable[hikari.ModalActionRowComponent]
                   | Iterable[hikari.ModalComponentTypesT]
    ) -> tuple[ComponentStateBase, ...]:
        if isinstance(component, (list, tuple)):
            return tuple(
                state
                for child in component
                for state in self.__transform_modal_component_state(interaction, child)
            )

        if isinstance(component, hikari.ActionRowComponent):
            return self.__transform_modal_component_state(interaction, component.components)

        if isinstance(component, hikari.TextInputComponent):
            return (self.__transform_text_box_state(component.custom_id, component.value),)

        raise ArgumentError("component", f"Unknown modal component type '{type(component)}'.")

    def __transform_stack_layout(
        self,
        component: StackLayout,
        container: endpointsintf.ComponentBuilder | None
    ) -> endpointsintf.ComponentBuilder:
        if container:
            raise ArgumentError("A stack layout cannot be placed in a container layout.")

        child_count = len(component.children)
        assert_range(child_count, 0, 5, "component.children")

        for child in component.children:
            match child:
                case StackLayout():
                    raise ArgumentError("component.children", "A stack layout cannot contain another stack layout as its child.")
                case ComboBox() if child_count > 1:
                    raise ArgumentError("component.children", "A stack layout cannot contain more than one child when it contains a combo box.")

        builder = endpoints.MessageActionRowBuilder()
        for child in component.children:
            self.__transform_component(child, builder)

        return builder

    def __transform_button(
        self,
        component: Button,
        container: endpointsintf.ComponentBuilder | None
    ) -> endpointsintf.ComponentBuilder:
        assert_not_none(container, "container")
        if not component.emoji_id:
            assert_not_none(component.text, "component.text")
            assert_range(len(cast(str, component.text)), 1, 80, "component.text")
        if not isinstance(container, endpoints.MessageActionRowBuilder):
            raise ArgumentError(f"A button can only be placed in an action row, but got '{type(container)}'.")
        if not component.text and not component.emoji_id:
            raise ArgumentError("component", "At least one of the button's text or emoji must be specified.")

        if component.style is ComponentStyle.LINK:
            if not component.url:
                raise ArgumentError(f"The URL of the link-style button '{component.id}' must be specified.")

            button = container.add_link_button(
                component.url,
                emoji=int(component.emoji_id) if component.emoji_id else hikari.UNDEFINED,
                label=component.text or hikari.UNDEFINED,
                is_disabled=not component.is_enabled
            )
        else:
            custom_data = ";".join((f"{key}={value}" for key, value in component.custom_data.items()))
            button = container.add_interactive_button(
                COMPONENT_STYLE_MAP.get(component.style, hikari.ButtonStyle.PRIMARY),
                f"{component.id}~{component.owner_id};{custom_data}",
                emoji=int(component.emoji_id) if component.emoji_id else hikari.UNDEFINED,
                label=component.text or hikari.UNDEFINED,
                is_disabled=not component.is_enabled
            )

        return button

    def __transform_button_state(self, interaction: hikari.ComponentInteraction) -> ButtonState:
        component_data = ComponentTransformer.__get_component_data_from_custom_id(interaction.custom_id)
        parts = component_data.data.split(";")
        if len(parts) < 2:
            raise ValueError("Invalid component state. Required 'owner_id' is missing for the button.")

        custom_data = {}
        for mapping in islice(parts, 1, None):
            mapping_parts = mapping.split("=", maxsplit=1)
            if len(mapping_parts) != 2:
                continue

            custom_data[mapping_parts[0]] = mapping_parts[1]

        return ButtonState(
            identifier=component_data.identifier,
            owner_id=parts[0],
            custom_data=custom_data
        )

    def __transform_combo_box(
        self,
        component: ComboBox,
        container: endpointsintf.ComponentBuilder | None
    ) -> endpointsintf.ComponentBuilder:
        assert_not_none(container, "container")
        assert_range(len(component.items), 1, 25, "component.items")
        assert_range(component.selection_count_min, 1, 25, "component.selection_count_min")
        assert_range(component.selection_count_max, 1, 25, "component.selection_count_max")
        if not isinstance(container, endpoints.MessageActionRowBuilder):
            raise ArgumentError(f"A button can only be placed in an action row, but got '{type(container)}'.")
        if component.selection_count_max < component.selection_count_min:
            raise ArgumentError("component.selection_count_max", "The maximum number of selected items must be greater than or equal to the minimum.")

        builder = container.add_text_menu(component.id)
        if component.placeholder:
            builder.set_placeholder(component.placeholder)
        builder.set_min_values(component.selection_count_min)
        builder.set_max_values(component.selection_count_max)
        builder.set_is_disabled(not component.is_enabled)
        for item in component.items:
            builder.add_option(
                item.text,
                f"{component.owner_id};{item.value}",
                description=item.description or hikari.UNDEFINED
            )

        return builder

    def __transform_combo_box_state(self, interaction: hikari.ComponentInteraction) -> ComboBoxState:
        selected_values = []
        owner_id = None
        for value in interaction.values:
            parts = value.split(";", maxsplit=1)
            if len(parts) < 2:
                raise ValueError("Invalid component state. Required 'owner_id' is missing for the combo box.")

            owner_id = parts[0]
            selected_values.append(parts[1])

        if not owner_id:
            raise ValueError("Invalid component state. Required 'owner_id' is missing for the combo box.")

        return ComboBoxState(
            identifier=interaction.custom_id,
            owner_id=owner_id,
            selected_values=selected_values
        )

    def __transform_pager(
        self,
        component: Paginator,
        container: endpointsintf.ComponentBuilder | None
    ) -> endpointsintf.ComponentBuilder:
        assert_not_none(component, "component")
        if container:
            raise ArgumentError(f"A pager is a layout and cannot be placed in another layout, but was placed in '{type(container)}'.")

        previous_button_custom_data = {
            "page": str(component.current_page - 1),
            **component.custom_data
        }

        next_button_custom_data = {
            "page": str(component.current_page + 1),
            **component.custom_data
        }

        return self.__transform_component(
            StackLayout(
                id=component.id,
                children=[
                    Button(
                        id=component.id,
                        owner_id=component.owner_id,
                        text=None if self.__options.value.PaginatorPreviousEmoji else "Previous",
                        style=ComponentStyle.SECONDARY,
                        is_enabled=not component.is_first_page(),
                        emoji_id=self.__options.value.PaginatorPreviousEmoji,
                        custom_data=previous_button_custom_data
                    ),
                    Button(
                        id=component.id,
                        owner_id=component.owner_id,
                        text=None if self.__options.value.PaginatorNextEmoji else "Next",
                        style=ComponentStyle.SECONDARY,
                        is_enabled=not component.is_last_page(),
                        emoji_id=self.__options.value.PaginatorNextEmoji,
                        custom_data=next_button_custom_data
                    )
                ]
            ),
            None
        )

    def __transform_pager_state(self, interaction: hikari.ComponentInteraction) -> PagerState:
        # Pager states are currently button clicks only.
        state = self.__transform_button_state(interaction)

        return PagerState(
            identifier=state.identifier,
            owner_id=state.owner_id,
            current_page=try_parse_int(state.custom_data.pop("page", "0")) or 0,
            custom_data=state.custom_data
        )

    def __transform_text_box(
        self,
        component: TextBox,
        container: endpointsintf.ComponentBuilder | None
    ) -> endpointsintf.ComponentBuilder:
        assert_not_none(container, "container")
        assert_range(len(component.label), 1, 45, "component.label")
        assert_range(component.min_length, 0, 4000, "component.min_length")
        assert_range(component.max_length, 1, 4000, "component.max_length")
        if component.placeholder is not None:
            assert_range(len(component.placeholder), 0, 100, "component.placeholder")
        if component.default_value is not None:
            assert_range(len(component.default_value), 0, 4000, "component.default_value")

        if not isinstance(container, endpoints.ModalActionRowBuilder):
            raise ArgumentError(f"A button can only be placed in a modal, but got '{type(container)}'.")

        builder = container.add_text_input(
            f"{component.id}~{component.owner_id}",
            component.label,
            style=hikari.TextInputStyle.PARAGRAPH if component.style is TextBoxStyle.MULTI_LINE else hikari.TextInputStyle.SHORT,
            placeholder=component.placeholder or hikari.UNDEFINED,
            value=component.default_value or hikari.UNDEFINED,
            required=component.is_required,
            min_length=component.min_length,
            max_length=component.max_length
        )

        return builder

    def __transform_text_box_state(self, custom_id: str, value: str) -> TextBoxState:
        component_data = ComponentTransformer.__get_component_data_from_custom_id(custom_id)
        parts = component_data.data.split(";", maxsplit=1)
        if len(parts) < 1:
            raise ValueError("Invalid component state. Required 'owner_id' is missing for the text box state.")

        if not parts[0]:
            raise ValueError("Invalid component state. Required 'owner_id' is missing for the text box state.")

        return TextBoxState(
            identifier=component_data.identifier,
            owner_id=parts[0],
            value=escape_user_input(value)
        )
