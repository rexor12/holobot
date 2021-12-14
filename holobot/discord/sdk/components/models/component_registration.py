from .component_interaction_response import ComponentInteractionResponse
from ..component import Component
from ...models import InteractionContext
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Type

@dataclass
class ComponentRegistration:
    id: str
    component_type: Type[Component]
    on_interaction: Callable[['ComponentRegistration', InteractionContext, Any], Awaitable[ComponentInteractionResponse]]
