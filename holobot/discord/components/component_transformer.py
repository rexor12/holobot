from .icomponent_transformer import IComponentTransformer
from holobot.discord.sdk.components import Button, ComboBox, Component, StackLayout
from holobot.discord.sdk.components.enums import ComponentStyle
from holobot.discord.sdk.components.models import ComboBoxState, DEFAULT_EMPTY_STATE
from holobot.sdk.exceptions import ArgumentError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none, assert_range
from typing import Any, Callable, Dict, Type

PRIMARY_COMPONENT_STYLE_ID: int = 1

COMPONENT_STYLE_IDS: Dict[ComponentStyle, int] = {
    ComponentStyle.PRIMARY: PRIMARY_COMPONENT_STYLE_ID,
    ComponentStyle.SECONDARY: 2,
    ComponentStyle.SUCCESS: 3,
    ComponentStyle.DANGER: 4,
    ComponentStyle.LINK: 5
}

@injectable(IComponentTransformer)
class ComponentTransformer(IComponentTransformer):
    def __init__(self) -> None:
        super().__init__()
        self.__component_transformers: Dict[Type[Component], Callable[[Any], Dict[str, Any]]] = {
            StackLayout: self.__transform_stack_layout,
            Button: self.__transform_button,
            ComboBox: self.__transform_combo_box
        }
        self.__state_transformers: Dict[Type[Component], Callable[[Dict[str, Any]], Any]] = {
            StackLayout: lambda _: DEFAULT_EMPTY_STATE,
            Button: lambda _: DEFAULT_EMPTY_STATE,
            ComboBox: self.__transform_combo_box_state
        }

    def transform_component(self, component: Component) -> Dict[str, Any]:
        assert_not_none(component, "component")
        assert_range(len(component.id), 1, 100, "component.id")

        if not (transformer := self.__component_transformers.get(type(component), None)):
            raise ArgumentError("component", "Invalid component type.")
        return transformer(component)

    def transform_state(self, component_type: Type[Component], json: Dict[str, Any]) -> Any:
        assert_not_none(component_type, "component_type")
        assert_not_none(json, "json")

        if not (transformer := self.__state_transformers.get(component_type, None)):
            raise ArgumentError("component_type", "Invalid component type.")
        return transformer(json)

    def __transform_stack_layout(self, component: StackLayout) -> Dict[str, Any]:
        child_count = len(component.children)
        assert_range(child_count, 0, 5, "component.children")

        for child in component.children:
            if isinstance(child, StackLayout):
                raise ArgumentError("component.children", "A stack layout cannot contain another stack layout as its child.")
            if isinstance(child, ComboBox) and child_count > 1:
                raise ArgumentError("component.children", "A stack layout cannot contain more than one child when it contains a combo box.")

        return {
            "type": 1,
            "components": [self.transform_component(child) for child in component.children]
        }

    def __transform_button(self, component: Button) -> Dict[str, Any]:
        assert_range(len(component.text), 1, 80, "component.text")

        style = component.style if not component.url else ComponentStyle.LINK
        id = component.id if component.style != ComponentStyle.LINK else None
        return {
            "type": 2,
            "custom_id": id,
            "style": COMPONENT_STYLE_IDS.get(style, PRIMARY_COMPONENT_STYLE_ID),
            "label": component.text,
            "disabled": not component.is_enabled,
            "url": component.url
        }

    def __transform_combo_box(self, component: ComboBox) -> Dict[str, Any]:
        assert_range(len(component.items), 1, 25, "component.items")
        assert_range(component.selection_count_min, 1, 25, "component.selection_count_min")
        assert_range(component.selection_count_max, 1, 25, "component.selection_count_max")
        if component.selection_count_max < component.selection_count_min:
            raise ArgumentError("component.selection_count_max", "The maximum number of selected items must be greater than or equal to the minimum.")

        return {
            "type": 3,
            "custom_id": component.id,
            "options": [{
                "label": item.text,
                "value": item.value,
                "description": item.description
            } for item in component.items],
            "placeholder": component.placeholder,
            "min_values": component.selection_count_min,
            "max_values": component.selection_count_max,
            "disabled": not component.is_enabled
        }

    def __transform_combo_box_state(self, json: Dict[str, Any]) -> ComboBoxState:
        return ComboBoxState(
            selected_values=json.get("values", [])
        )
