from collections.abc import Callable, Generator, Iterable, Sequence
from typing import Any, NamedTuple, cast

import hikari
import hikari.api.special_endpoints as special_endpoints
import hikari.impl.special_endpoints as endpoints

from holobot.discord import DiscordOptions
from holobot.discord.sdk.workflows.interactables.components import (
    Button, ButtonState, ComboBox, ComboBoxState, ComponentBase, ComponentStateBase, ComponentStyle,
    LayoutBase, Paginator, PaginatorState, RoleSelector, RoleSelectorState, StackLayout, TextBox,
    TextBoxState, TextBoxStyle
)
from holobot.discord.sdk.workflows.interactables.views import Modal, ModalState
from holobot.discord.transformers.emoji import to_model as emoji_to_model
from holobot.sdk.configs import IOptions
from holobot.sdk.exceptions import ArgumentError
from holobot.sdk.ioc import injectable
from holobot.sdk.utils.exception_utils import assert_not_none, assert_range
from holobot.sdk.utils.string_utils import try_parse_int
from .icomponent_transformer import ComponentId, IComponentTransformer

_COMPONENT_STYLE_MAP: dict[ComponentStyle, hikari.InteractiveButtonTypesT] = {
    ComponentStyle.PRIMARY: hikari.ButtonStyle.PRIMARY,
    ComponentStyle.SECONDARY: hikari.ButtonStyle.SECONDARY,
    ComponentStyle.SUCCESS: hikari.ButtonStyle.SUCCESS,
    ComponentStyle.DANGER: hikari.ButtonStyle.DANGER
}

_TComponentBuilder = Callable[
    [Any, special_endpoints.ComponentBuilder | None, dict[str, int]],
    special_endpoints.ComponentBuilder
]

class _ControlData(NamedTuple):
    identifier: str
    index: int
    owner_id: str
    version: int
    custom_data: dict[str, str]

@injectable(IComponentTransformer)
class ComponentTransformer(IComponentTransformer):
    def __init__(self, options: IOptions[DiscordOptions]) -> None:
        super().__init__()
        self.__options = options
        self.__control_transformers: dict[type[ComponentBase], _TComponentBuilder] = {
            StackLayout: self.__add_stack_layout,
            Paginator: self.__add_paginator,
            Button: self.__add_button,
            ComboBox: self.__add_combo_box,
            TextBox: self.__add_text_box,
            RoleSelector: self.__add_role_selector
        }

    def create_controls(
        self,
        controls: ComponentBase | Sequence[LayoutBase]
    ) -> list[special_endpoints.ComponentBuilder]:
        match controls:
            case LayoutBase():
                controls = [controls]
            case ComponentBase():
                controls = [StackLayout(id="auto_wrapper_stack_layout", children=[controls])]
            case list() if len(controls) > 5:
                raise ArgumentError("controls", "A message cannot hold more than 5 layouts.")

        counters = dict[str, int]()

        return list(map(
            lambda c: self.__create_control(c, None, counters),
            controls
        ))

    def create_modal(
        self,
        view: Modal
    ) -> list[special_endpoints.ModalActionRowBuilder]:
        assert_range(len(view.title), 1, 45, "view.title")
        assert_range(len(view.components), 1, 5, "view.children")

        builders = []
        counters = dict[str, int]()
        for child in view.components:
            if not isinstance(child, TextBox):
                raise ArgumentError("view.components", f"A modal cannot have a '{type(child)}' as its child.")

            builder = endpoints.ModalActionRowBuilder()
            self.__add_text_box(child, builder, counters)
            builders.append(builder)

        return builders

    def create_modal_state(
        self,
        interaction: hikari.ModalInteraction
    ) -> ModalState:
        return ModalState(
            owner_id=str(interaction.user.id),
            components={
                state.identifier: state
                for state in self.__create_modal_control_states(interaction, interaction.components)
            }
        )

    def create_control_states(
        self,
        interaction: hikari.ComponentInteraction,
        expected_target_types: dict[str, type[ComponentStateBase]]
    ) -> Sequence[ComponentStateBase]:
        states = list[ComponentStateBase]()
        for control in interaction.message.components:
            created_states = self.__create_control_states_internal(
                interaction,
                control,
                expected_target_types
            )
            for state in created_states:
                states.append(state)

        return states

    def get_component_id(self, custom_id: str) -> ComponentId:
        separator_index = custom_id.find("~")
        if separator_index < 0:
            separator_index = len(custom_id)

        subseparator_index = custom_id.find(":", 0, separator_index)
        if subseparator_index < 1:
            raise ArgumentError(
                "custom_id",
                f"Missing 'index' part in component identifier '{custom_id}'."
            )

        component_index_string = custom_id[subseparator_index + 1:separator_index]
        if (component_index := try_parse_int(component_index_string)) is None:
            raise ArgumentError(
                "custom_id",
                f"Cannot parse value as 'index' in component identifier '{custom_id}'."
            )

        return ComponentId(custom_id[:subseparator_index], component_index)

    @staticmethod
    def __unpack_custom_data(custom_id: str) -> _ControlData:
        custom_id_parts = custom_id.split("~")
        if len(custom_id_parts) < 4:
            raise ArgumentError(
                "custom_id",
                "Invalid control state: some fields are missing."
            )

        component_id_parts = custom_id_parts[0].split(":", 1)
        if len(component_id_parts) != 2:
            raise ArgumentError(
                "custom_id",
                "The component identifier is missing the required index property."
            )

        if (component_index := try_parse_int(component_id_parts[1])) is None:
            raise ArgumentError(
                "custom_id",
                f"The component index '{component_id_parts[1]}' is not a valid integer."
            )

        if (version := try_parse_int(custom_id_parts[2])) is None:
            raise ArgumentError(
                "custom_id",
                "Invalid control state. Failed to parse control state version."
            )

        custom_data = dict[str, str]()
        for mapping in custom_id_parts[3].split(";"):
            key_value = mapping.split("=", maxsplit=1)
            if len(key_value) != 2:
                continue

            custom_data[key_value[0]] = key_value[1]

        return _ControlData(
            component_id_parts[0],
            component_index,
            custom_id_parts[1],
            version,
            custom_data
        )

    @staticmethod
    def __pack_custom_data(
        identifier: str,
        index: int,
        owner_id: str,
        version: int,
        custom_data: dict[str, str]
    ) -> str:
        custom_data_part = ";".join(
            f"{key}={value}"
            for key, value in custom_data.items()
        )

        return f"{identifier}:{index}~{owner_id}~{version}~{custom_data_part}"

    @staticmethod
    def __assert_control_type(
        valid_control_types: Sequence[type[ComponentStateBase]],
        target_control_type: type[ComponentStateBase] | None,
        control_id: str
    ) -> None:
        if target_control_type and target_control_type not in valid_control_types:
            raise TypeError((
                f"Expected control with identifier '{control_id}'"
                f" to be of type '{target_control_type}' which is invalid for this control."
            ))

    @staticmethod
    def __increment_counter(
        counters: dict[str, int],
        component_id: str
    ) -> int:
        counter = counters.get(component_id, 0)
        counters[component_id] = counter + 1

        return counter

    def __create_control(
        self,
        control: ComponentBase,
        container: special_endpoints.ComponentBuilder | None,
        counters: dict[str, int]
    ) -> special_endpoints.ComponentBuilder:
        assert_range(len(control.id), 1, 100, "control.id")

        if not (transformer := self.__control_transformers.get(type(control))):
            raise ArgumentError("control", "Invalid component type.")

        return transformer(control, container, counters)

    def __create_control_states_internal(
        self,
        interaction: hikari.ComponentInteraction,
        control: hikari.PartialComponent,
        expected_target_types: dict[str, type[ComponentStateBase]]
    ) -> Generator[ComponentStateBase, Any, None]:
        if isinstance(control, hikari.ActionRowComponent):
            for child in control.components:
                # TODO Restore StackLayout.
                results = self.__create_control_states_internal(
                    interaction,
                    child,
                    expected_target_types
                )
                for result in results:
                    yield result
            return

        if isinstance(control, hikari.ButtonComponent):
            yield self.__create_button_state(control, expected_target_types)
            return

        if isinstance(control, hikari.SelectMenuComponent):
            # NOTE: Discord only provides the select menu's options
            # if this component is the interaction source.
            values = (
                interaction.values or ()
                if control.custom_id == interaction.custom_id
                else ()
            )
            if control.type is hikari.ComponentType.ROLE_SELECT_MENU:
                yield self.__create_role_selector_state(control, expected_target_types, values)
                return

            yield self.__create_combo_box_state(control, expected_target_types, values)
            return

        if isinstance(control, hikari.TextInputComponent):
            yield self.__create_text_box_state(control, expected_target_types)
            return

        raise ArgumentError("control", f"Unknown control type '{type(control)}'.")

    def __create_modal_control_states(
        self,
        interaction: hikari.ModalInteraction,
        control: hikari.ModalActionRowComponent
                 | hikari.ModalComponentTypesT
                 | Iterable[hikari.ModalActionRowComponent]
                 | Iterable[hikari.ModalComponentTypesT]
    ) -> tuple[ComponentStateBase, ...]:
        if isinstance(control, (list, tuple)):
            return tuple(
                state
                for child in control
                for state in self.__create_modal_control_states(interaction, child)
            )

        if isinstance(control, hikari.ActionRowComponent):
            return self.__create_modal_control_states(interaction, control.components)

        if isinstance(control, hikari.TextInputComponent):
            return (self.__create_text_box_state(control, {}),)

        raise ArgumentError("control", f"Unknown modal control type '{type(control)}'.")

    def __add_stack_layout(
        self,
        control: StackLayout,
        container: special_endpoints.ComponentBuilder | None,
        counters: dict[str, int]
    ) -> special_endpoints.ComponentBuilder:
        if container:
            raise ArgumentError("A stack layout cannot be placed in a container layout.")

        child_count = len(control.children)
        assert_range(child_count, 0, 5, "control.children")

        for child in control.children:
            match child:
                case StackLayout():
                    raise ArgumentError("control.children", "A stack layout cannot contain another stack layout as its child.")
                case ComboBox() if child_count > 1:
                    raise ArgumentError("control.children", "A stack layout cannot contain more than one child when it contains a combo box.")

        builder = endpoints.MessageActionRowBuilder()
        for child in control.children:
            self.__create_control(child, builder, counters)

        return builder

    def __add_button(
        self,
        control: Button,
        container: special_endpoints.ComponentBuilder | None,
        counters: dict[str, int]
    ) -> special_endpoints.ComponentBuilder:
        assert_not_none(container, "container")
        if not control.emoji_id:
            assert_not_none(control.text, "control.text")
            assert_range(len(cast(str, control.text)), 1, 80, "control.text")
        if not isinstance(container, endpoints.MessageActionRowBuilder):
            raise ArgumentError(f"A button can only be placed in an action row, but got '{type(container)}'.")
        if not control.text and not control.emoji_id:
            raise ArgumentError("control", "At least one of the button's text or emoji must be specified.")

        if control.style is ComponentStyle.LINK:
            if not control.url:
                raise ArgumentError(f"The URL of the link-style button '{control.id}' must be specified.")

            return container.add_link_button(
                control.url,
                emoji=int(control.emoji_id) if control.emoji_id else hikari.UNDEFINED,
                label=control.text or hikari.UNDEFINED,
                is_disabled=not control.is_enabled
            )

        return container.add_interactive_button(
            _COMPONENT_STYLE_MAP.get(control.style, hikari.ButtonStyle.PRIMARY),
            ComponentTransformer.__pack_custom_data(
                control.id,
                ComponentTransformer.__increment_counter(counters, control.id),
                control.owner_id,
                0,
                control.custom_data
            ),
            emoji=int(control.emoji_id) if control.emoji_id else hikari.UNDEFINED,
            label=control.text or hikari.UNDEFINED,
            is_disabled=not control.is_enabled
        )

    def __create_button_state(
        self,
        control: hikari.ButtonComponent,
        expected_target_types: dict[str, type[ComponentStateBase]]
    ) -> ButtonState | PaginatorState:
        # Link buttons don't have identifiers as they don't trigger interactions.
        if not control.custom_id:
            return ButtonState(
                identifier="dummy",
                owner_id="dummy",
                custom_data={},
                emoji=None
            )

        data = ComponentTransformer.__unpack_custom_data(control.custom_id)
        expected_target_type = expected_target_types.get(data.identifier)
        if expected_target_type is PaginatorState:
            return PaginatorState(
                identifier=data.identifier,
                owner_id=data.owner_id,
                current_page=try_parse_int(data.custom_data.pop("page", "0")) or 0,
                custom_data=data.custom_data
            )

        ComponentTransformer.__assert_control_type((ButtonState,), expected_target_type, data.identifier)

        return ButtonState(
            identifier=data.identifier,
            owner_id=data.owner_id,
            emoji=emoji_to_model(control.emoji) if control.emoji else None,
            custom_data=data.custom_data
        )

    def __add_paginator(
        self,
        control: Paginator,
        container: special_endpoints.ComponentBuilder | None,
        counters: dict[str, int]
    ) -> special_endpoints.ComponentBuilder:
        assert_not_none(control, "control")
        if container:
            raise ArgumentError(f"A paginator is a layout and cannot be placed in another layout, but was placed in '{type(container)}'.")

        previous_button_custom_data = {
            "page": str(control.current_page - 1),
            **control.custom_data
        }

        next_button_custom_data = {
            "page": str(control.current_page + 1),
            **control.custom_data
        }

        # TODO Use the counter value?
        # ComponentTransformer.__increment_counter(counters, control.id)

        return self.__add_stack_layout(
            StackLayout(
                id=control.id,
                children=[
                    Button(
                        id=control.id,
                        owner_id=control.owner_id,
                        text=None if self.__options.value.PaginatorPreviousEmoji else "Previous",
                        style=ComponentStyle.SECONDARY,
                        is_enabled=not control.is_first_page(),
                        emoji_id=self.__options.value.PaginatorPreviousEmoji,
                        custom_data=previous_button_custom_data
                    ),
                    Button(
                        id=control.id,
                        owner_id=control.owner_id,
                        text=None if self.__options.value.PaginatorNextEmoji else "Next",
                        style=ComponentStyle.SECONDARY,
                        is_enabled=not control.is_last_page(),
                        emoji_id=self.__options.value.PaginatorNextEmoji,
                        custom_data=next_button_custom_data
                    )
                ]
            ),
            None,
            counters
        )

    def __add_role_selector(
        self,
        control: RoleSelector,
        container: special_endpoints.ComponentBuilder | None,
        counters: dict[str, int]
    ) -> special_endpoints.ComponentBuilder:
        assert_not_none(container, "control")
        assert_range(control.selection_count_min, 1, 25, "control.selection_count_min")
        assert_range(control.selection_count_max, 1, 25, "control.selection_count_max")
        if not isinstance(container, endpoints.MessageActionRowBuilder):
            raise ArgumentError(f"A role selector can only be placed in an action row, but got '{type(container)}'.")
        if control.selection_count_max < control.selection_count_min:
            raise ArgumentError("control.selection_count_max", "The maximum number of selected items must be greater than or equal to the minimum.")

        builder = container.add_select_menu(
            hikari.ComponentType.ROLE_SELECT_MENU,
            ComponentTransformer.__pack_custom_data(
                control.id,
                ComponentTransformer.__increment_counter(counters, control.id),
                control.owner_id,
                0,
                control.custom_data
            ),
            placeholder=control.placeholder or hikari.UNDEFINED,
            min_values=control.selection_count_min,
            max_values=control.selection_count_max,
            is_disabled=not control.is_enabled
        )

        return builder

    def __create_role_selector_state(
        self,
        control: hikari.SelectMenuComponent,
        expected_target_types: dict[str, type[ComponentStateBase]],
        selected_values: Sequence[str]
    ) -> RoleSelectorState:
        data = ComponentTransformer.__unpack_custom_data(control.custom_id)
        expected_target_type = expected_target_types.get(data.identifier)
        ComponentTransformer.__assert_control_type((RoleSelectorState,), expected_target_type, data.identifier)

        return RoleSelectorState(
            identifier=data.identifier,
            owner_id=data.owner_id,
            selected_values=selected_values,
            custom_data=data.custom_data
        )

    def __add_combo_box(
        self,
        control: ComboBox,
        container: special_endpoints.ComponentBuilder | None,
        counters: dict[str, int]
    ) -> special_endpoints.ComponentBuilder:
        assert_not_none(container, "control")
        assert_range(len(control.items), 1, 25, "control.items")
        assert_range(control.selection_count_min, 1, 25, "control.selection_count_min")
        assert_range(control.selection_count_max, 1, 25, "control.selection_count_max")
        if not isinstance(container, endpoints.MessageActionRowBuilder):
            raise ArgumentError(f"A combo box can only be placed in an action row, but got '{type(container)}'.")
        if control.selection_count_max < control.selection_count_min:
            raise ArgumentError("control.selection_count_max", "The maximum number of selected items must be greater than or equal to the minimum.")

        builder = container.add_text_menu(
            ComponentTransformer.__pack_custom_data(
                control.id,
                ComponentTransformer.__increment_counter(counters, control.id),
                control.owner_id,
                0,
                {}
            )
        )
        if control.placeholder:
            builder.set_placeholder(control.placeholder)
        builder.set_min_values(control.selection_count_min)
        builder.set_max_values(control.selection_count_max)
        builder.set_is_disabled(not control.is_enabled)
        for item in control.items:
            builder.add_option(
                item.text,
                item.value,
                description=item.description or hikari.UNDEFINED
            )

        return builder

    def __create_combo_box_state(
        self,
        control: hikari.SelectMenuComponent,
        expected_target_types: dict[str, type[ComponentStateBase]],
        selected_values: Sequence[str]
    ) -> ComboBoxState:
        data = ComponentTransformer.__unpack_custom_data(control.custom_id)
        expected_target_type = expected_target_types.get(data.identifier)
        ComponentTransformer.__assert_control_type((ComboBoxState,), expected_target_type, data.identifier)

        return ComboBoxState(
            identifier=data.identifier,
            owner_id=data.owner_id,
            selected_values=selected_values
        )

    def __add_text_box(
        self,
        control: TextBox,
        container: special_endpoints.ComponentBuilder | None,
        counters: dict[str, int]
    ) -> special_endpoints.ComponentBuilder:
        assert_not_none(container, "container")
        assert_range(len(control.label), 1, 45, "control.label")
        assert_range(control.min_length, 0, 4000, "control.min_length")
        assert_range(control.max_length, 1, 4000, "control.max_length")
        if control.placeholder is not None:
            assert_range(len(control.placeholder), 0, 100, "control.placeholder")
        if control.default_value is not None:
            assert_range(len(control.default_value), 0, 4000, "control.default_value")
        if not isinstance(container, endpoints.ModalActionRowBuilder):
            raise ArgumentError("container", f"A text box can only be placed in a modal, but got '{type(container)}'.")

        builder = container.add_text_input(
            ComponentTransformer.__pack_custom_data(
                control.id,
                ComponentTransformer.__increment_counter(counters, control.id),
                control.owner_id,
                0,
                control.custom_data
            ),
            control.label,
            style=hikari.TextInputStyle.PARAGRAPH if control.style is TextBoxStyle.MULTI_LINE else hikari.TextInputStyle.SHORT,
            placeholder=control.placeholder or hikari.UNDEFINED,
            value=control.default_value or hikari.UNDEFINED,
            required=control.is_required,
            min_length=control.min_length,
            max_length=control.max_length
        )

        return builder

    def __create_text_box_state(
        self,
        control: hikari.TextInputComponent,
        expected_target_types: dict[str, type[ComponentStateBase]]
    ) -> TextBoxState:
        data = ComponentTransformer.__unpack_custom_data(control.custom_id)
        expected_target_type = expected_target_types.get(data.identifier)
        ComponentTransformer.__assert_control_type((TextBoxState,), expected_target_type, data.identifier)

        return TextBoxState(
            identifier=data.identifier,
            owner_id=data.owner_id,
            value=control.value,
            custom_data=data.custom_data
        )
