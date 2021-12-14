from holobot.discord.sdk.components import Component
from typing import Any, Dict, Type

class IComponentTransformer:
    def transform_component(self, component: Component) -> Dict[str, Any]:
        raise NotImplementedError

    def transform_state(self, component_type: Type[Component], json: Dict[str, Any]) -> Any:
        raise NotImplementedError
