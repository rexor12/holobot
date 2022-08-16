from collections.abc import Callable
from typing import Any, NamedTuple, Type

import hikari
import hikari.api.special_endpoints as endpointsintf
import hikari.impl.special_endpoints as endpoints
import hikari.messages as hikari_messages

from holobot.discord.sdk.workflows.interactables.components import (
    Button, ComboBox, ComponentBase, Layout, Paginator, StackLayout
)
from holobot.discord.sdk.workflows.interactables.components.enums import ComponentStyle
from holobot.discord.sdk.workflows.interactables.components.models import (
    ComboBoxState, ComponentStateBase, EmptyState, PagerState
)
from holobot.sdk.exceptions import ArgumentError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none, assert_range, try_parse_int
from .icomponent_transformer import IComponentTransformer

PRIMARY_COMPONENT_STYLE_ID: int = 1

COMPONENT_STYLE_MAP: dict[ComponentStyle, hikari_messages.ButtonStyle] = {
    ComponentStyle.PRIMARY: hikari_messages.ButtonStyle.PRIMARY,
    ComponentStyle.SECONDARY: hikari_messages.ButtonStyle.SECONDARY,
    ComponentStyle.SUCCESS: hikari_messages.ButtonStyle.SUCCESS,
    ComponentStyle.DANGER: hikari_messages.ButtonStyle.DANGER,
    ComponentStyle.LINK: hikari_messages.ButtonStyle.LINK
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
    def __init__(self) -> None:
        super().__init__()
        self.__component_transformers: dict[Type[ComponentBase], _TComponentBuilder] = {
            StackLayout: self.__transform_stack_layout,
            Button: self.__transform_button,
            ComboBox: self.__transform_combo_box,
            Paginator: self.__transform_pager
        }
        self.__state_transformers: dict[Type[ComponentBase], Callable[[hikari.ComponentInteraction], ComponentStateBase]] = {
            StackLayout: lambda i: EmptyState(owner_id=str(i.user.id)),
            Button: lambda i: EmptyState(owner_id=str(i.user.id)),
            ComboBox: self.__transform_combo_box_state,
            Paginator: self.__transform_pager_state
        }

    def transform_component(self, component: ComponentBase) -> endpointsintf.ComponentBuilder:
        return self.__transform_component(component, None)

    def transform_to_root_component(
        self,
        components: ComponentBase | list[Layout]
    ) -> list[endpointsintf.ComponentBuilder]:
        if not components:
            return []

        if isinstance(components, list):
            if len(components) == 0:
                return []
        elif not isinstance(components, Layout):
            components = [StackLayout(id="auto_wrapper_stack_layout", children=[components])]
        else: components = [components]

        if len(components) > 5:
            raise ArgumentError("components", "A message cannot hold more than 5 layouts.")

        return [
            self.transform_component(component)
            for component in components
        ]

    def transform_state(
        self,
        component_type: Type[ComponentBase],
        interaction: hikari.ComponentInteraction
    ) -> ComponentStateBase:
        assert_not_none(component_type, "component_type")
        assert_not_none(interaction, "interaction")

        if not (transformer := self.__state_transformers.get(component_type, None)):
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

        if not (transformer := self.__component_transformers.get(type(component), None)):
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
            if isinstance(child, StackLayout):
                raise ArgumentError("component.children", "A stack layout cannot contain another stack layout as its child.")
            if isinstance(child, ComboBox) and child_count > 1:
                raise ArgumentError("component.children", "A stack layout cannot contain more than one child when it contains a combo box.")

        builder = endpoints.ActionRowBuilder()
        for child in component.children:
            self.__transform_component(child, builder)

        return builder

    def __transform_button(
        self,
        component: Button,
        container: endpointsintf.ComponentBuilder | None
    ) -> endpointsintf.ComponentBuilder:
        assert_not_none(container, "container")
        assert_range(len(component.text), 1, 80, "component.text")
        if not isinstance(container, endpoints.ActionRowBuilder):
            raise ArgumentError(f"A button can only be placed in an action row, but got '{type(container)}'.")

        if component.style == ComponentStyle.LINK:
            if not component.url:
                raise ArgumentError(f"The URL of the link-style button '{component.id}' must be specified.")

            return container.add_button(
                hikari_messages.ButtonStyle.LINK,
                component.url
            ).set_label(component.text).set_is_disabled(not component.is_enabled).add_to_container()

        return container.add_button(
            COMPONENT_STYLE_MAP.get(component.style, hikari_messages.ButtonStyle.PRIMARY),
            component.id
        ).set_label(component.text).set_is_disabled(not component.is_enabled).add_to_container()

    def __transform_combo_box(
        self,
        component: ComboBox,
        container: endpointsintf.ComponentBuilder | None
    ) -> endpointsintf.ComponentBuilder:
        assert_not_none(container, "container")
        assert_range(len(component.items), 1, 25, "component.items")
        assert_range(component.selection_count_min, 1, 25, "component.selection_count_min")
        assert_range(component.selection_count_max, 1, 25, "component.selection_count_max")
        if not isinstance(container, endpoints.ActionRowBuilder):
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

    def __transform_combo_box_state(
        self,
        interaction: hikari.ComponentInteraction
    ) -> ComboBoxState:
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

        custom_data = ";".join((f"{key}={value}" for key, value in component.custom_data.items()))
        return self.__transform_component(
            StackLayout(
                id=component.id,
                children=[
                    # TODO Dedicated data field (implemented on the main/FreeEpicGamesCommand branch).
                    Button(
                        id=f"{component.id}~{component.current_page - 1};{component.owner_id};{custom_data}",
                        owner_id=component.owner_id,
                        text="Previous",
                        style=ComponentStyle.SECONDARY,
                        is_enabled=not component.is_first_page()
                    ),
                    Button(
                        id=f"{component.id}~{component.current_page + 1};{component.owner_id};{custom_data}",
                        owner_id=component.owner_id,
                        text="Next",
                        style=ComponentStyle.SECONDARY,
                        is_enabled=not component.is_last_page()
                    )
                ]
            ),
            None
        )

    def __transform_pager_state(
        self,
        interaction: hikari.ComponentInteraction
    ) -> PagerState:
        _, data = ComponentTransformer.__get_component_data_from_custom_id(interaction.custom_id)
        data_parts = data.split(";")
        if len(data_parts) < 2:
            raise ValueError("Invalid component state. Required 'current_page' and 'owner_id' are missing for the paginator.")

        custom_data = {}
        for data_part in data_parts:
            custom_data_parts = data_part.split("=", 1)
            if len(custom_data_parts) == 2:
                custom_data[custom_data_parts[0]] = custom_data_parts[1]

        return PagerState(
            owner_id=data_parts[1],
            current_page=try_parse_int(data_parts[0]) or 0,
            custom_data=custom_data
        )
