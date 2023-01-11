from collections.abc import Callable
from itertools import islice
from typing import Any, NamedTuple, cast

import hikari
import hikari.api.special_endpoints as endpointsintf
import hikari.impl.special_endpoints as endpoints

from holobot.discord import DiscordOptions
from holobot.discord.sdk.workflows.interactables.components import (
    Button, ComboBox, ComponentBase, LayoutBase, Paginator, StackLayout
)
from holobot.discord.sdk.workflows.interactables.components.enums import ComponentStyle
from holobot.discord.sdk.workflows.interactables.components.models import (
    ButtonState, ComboBoxState, ComponentStateBase, EmptyState, PagerState
)
from holobot.sdk.configs import IOptions
from holobot.sdk.exceptions import ArgumentError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none, assert_range, try_parse_int
from .icomponent_transformer import IComponentTransformer

PRIMARY_COMPONENT_STYLE_ID: int = 1

COMPONENT_STYLE_MAP: dict[ComponentStyle, hikari.ButtonStyle] = {
    ComponentStyle.PRIMARY: hikari.ButtonStyle.PRIMARY,
    ComponentStyle.SECONDARY: hikari.ButtonStyle.SECONDARY,
    ComponentStyle.SUCCESS: hikari.ButtonStyle.SUCCESS,
    ComponentStyle.DANGER: hikari.ButtonStyle.DANGER,
    ComponentStyle.LINK: hikari.ButtonStyle.LINK
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
            Button: self.__transform_button,
            ComboBox: self.__transform_combo_box,
            Paginator: self.__transform_pager
        }
        self.__state_transformers: dict[type[ComponentBase], Callable[[hikari.ComponentInteraction], ComponentStateBase]] = {
            StackLayout: lambda i: EmptyState(owner_id=str(i.user.id)),
            Button: self.__transform_button_state,
            ComboBox: self.__transform_combo_box_state,
            Paginator: self.__transform_pager_state
        }

    def transform_component(self, component: ComponentBase) -> endpointsintf.ComponentBuilder:
        return self.__transform_component(component, None)

    def transform_to_root_component(self, components: ComponentBase | list[LayoutBase]) -> list[endpointsintf.ComponentBuilder]:
        match components:
            case LayoutBase():
                components = [components]
            case ComponentBase():
                components = [StackLayout(id="auto_wrapper_stack_layout", children=[components])]
            case list() if len(components) > 5:
                raise ArgumentError("components", "A message cannot hold more than 5 layouts.")
        return list(map(self.transform_component, components))

    def transform_state(
        self,
        component_type: type[ComponentBase],
        interaction: hikari.ComponentInteraction
    ) -> ComponentStateBase:
        assert_not_none(component_type, "component_type")
        assert_not_none(interaction, "interaction")

        if not (transformer := self.__state_transformers.get(component_type)):
            raise ArgumentError("component_type", "Invalid component type.")
        return transformer(interaction)

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

            button = container.add_button(hikari.ButtonStyle.LINK, component.url)
        else:
            custom_data = ";".join((f"{key}={value}" for key, value in component.custom_data.items()))
            button = container.add_button(
                COMPONENT_STYLE_MAP.get(component.style, hikari.ButtonStyle.PRIMARY),
                f"{component.id}~{component.owner_id};{custom_data}"
            )

        if component.text:
            button.set_label(component.text)

        if component.emoji_id:
            button.set_emoji(int(component.emoji_id))

        return button.set_is_disabled(not component.is_enabled).add_to_container()

    def __transform_button_state(self, interaction: hikari.ComponentInteraction) -> ButtonState:
        component_data = ComponentTransformer.__get_component_data_from_custom_id(interaction.custom_id)
        parts = component_data.data.split(";")
        if len(parts) < 2:
            raise ValueError("Invalid component state. Required 'owner_id' is missing for the button.")

        custom_data = {}
        for mapping in islice(parts, 2):
            mapping_parts = mapping.split("=", maxsplit=1)
            if len(mapping_parts) != 2:
                continue

            custom_data[mapping_parts[0]] = mapping_parts[1]

        return ButtonState(
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

        builder = container.add_select_menu(component.id)
        if component.placeholder:
            builder.set_placeholder(component.placeholder)
        builder.set_min_values(component.selection_count_min)
        builder.set_max_values(component.selection_count_max)
        builder.set_is_disabled(not component.is_enabled)
        for item in component.items:
            option_builder = builder.add_option(item.text, f"{component.owner_id};{item.value}")
            if item.description:
                option_builder.set_description(item.description)
            option_builder.add_to_menu()
        builder.add_to_container()

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
            owner_id=state.owner_id,
            current_page=try_parse_int(state.custom_data.pop("page", "0")) or 0,
            custom_data=state.custom_data
        )
