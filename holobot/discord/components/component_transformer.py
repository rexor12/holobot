from .icomponent_transformer import IComponentTransformer
from holobot.discord.sdk.components import Button, ComboBox, Component, StackLayout
from holobot.discord.sdk.components.enums import ComponentStyle
from holobot.discord.sdk.components.models import ComboBoxState, DEFAULT_EMPTY_STATE
from holobot.sdk.exceptions import ArgumentError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none, assert_range
from typing import Any, Callable, Dict, Optional, Type

import hikari
import hikari.messages as hikari_messages
import hikari.api.special_endpoints as endpointsintf
import hikari.impl.special_endpoints as endpoints

PRIMARY_COMPONENT_STYLE_ID: int = 1

COMPONENT_STYLE_MAP: Dict[ComponentStyle, hikari_messages.ButtonStyle] = {
    ComponentStyle.PRIMARY: hikari_messages.ButtonStyle.PRIMARY,
    ComponentStyle.SECONDARY: hikari_messages.ButtonStyle.SECONDARY,
    ComponentStyle.SUCCESS: hikari_messages.ButtonStyle.SUCCESS,
    ComponentStyle.DANGER: hikari_messages.ButtonStyle.DANGER,
    ComponentStyle.LINK: hikari_messages.ButtonStyle.LINK
}

_TComponentBuilder = Callable[
    [Any, Optional[endpointsintf.ComponentBuilder]],
    endpointsintf.ComponentBuilder
]

@injectable(IComponentTransformer)
class ComponentTransformer(IComponentTransformer):
    def __init__(self) -> None:
        super().__init__()
        self.__component_transformers: Dict[Type[Component], _TComponentBuilder] = {
            StackLayout: self.__transform_stack_layout,
            Button: self.__transform_button,
            ComboBox: self.__transform_combo_box
        }
        self.__state_transformers: Dict[Type[Component], Callable[[hikari.ComponentInteraction], Any]] = {
            StackLayout: lambda _: DEFAULT_EMPTY_STATE,
            Button: lambda _: DEFAULT_EMPTY_STATE,
            ComboBox: self.__transform_combo_box_state
        }

    def transform_component(self, component: Component) -> endpointsintf.ComponentBuilder:
        return self.__transform_component(component, None)

    def transform_state(
        self,
        component_type: Type[Component],
        interaction: hikari.ComponentInteraction
    ) -> Any:
        assert_not_none(component_type, "component_type")
        assert_not_none(interaction, "interaction")

        if not (transformer := self.__state_transformers.get(component_type, None)):
            raise ArgumentError("component_type", "Invalid component type.")
        return transformer(interaction)

    def __transform_component(
        self,
        component: Component,
        container: Optional[endpointsintf.ComponentBuilder]
    ) -> endpointsintf.ComponentBuilder:
        assert_not_none(component, "component")
        assert_range(len(component.id), 1, 100, "component.id")

        if not (transformer := self.__component_transformers.get(type(component), None)):
            raise ArgumentError("component", "Invalid component type.")

        return transformer(component, container)

    def __transform_stack_layout(
        self,
        component: StackLayout,
        container: Optional[endpointsintf.ComponentBuilder]
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
        container: Optional[endpointsintf.ComponentBuilder]
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
        container: Optional[endpointsintf.ComponentBuilder]
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
            option_builder = builder.add_option(item.text, item.value)
            if item.description:
                option_builder.set_description(item.description)
            option_builder.add_to_menu()
        builder.add_to_container()

        return builder

    def __transform_combo_box_state(
        self,
        interaction: hikari.ComponentInteraction
    ) -> ComboBoxState:
        return ComboBoxState(
            selected_values=interaction.values
        )
